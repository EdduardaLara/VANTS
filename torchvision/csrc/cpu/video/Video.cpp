
# include "Video.h"
#include <torch/script.h>
#include <c10/util/Logging.h>
#include "sync_decoder.h"
#include "sync_decoder.h"
#include "memory_buffer.h"
#include "defs.h"


using namespace std;
using namespace ffmpeg;


// If we are in a Windows environment, we need to define
// initialization functions for the _custom_ops extension
// #ifdef _WIN32
// #if PY_MAJOR_VERSION < 3
// PyMODINIT_FUNC init_video_reader(void) {
//   // No need to do anything.
//   return NULL;
// }
// #else
// PyMODINIT_FUNC PyInit_video_reader(void) {
//   // No need to do anything.
//   return NULL;
// }
// #endif
// #endif



const size_t decoderTimeoutMs = 600000;
const AVSampleFormat defaultAudioSampleFormat = AV_SAMPLE_FMT_FLT;
// A jitter can be added to the end of the range to avoid conversion/rounding
// error, small value 100us won't be enough to select the next frame, but enough
// to compensate rounding error due to the multiple conversions.
const size_t timeBaseJitterUs = 100;


// returns number of written bytes
template <typename T>
size_t fillTensorList(DecoderOutputMessage& msgs,
                      torch::Tensor& frame,
                      torch::Tensor& framePts) {
    // if (!msg) {
    //     return 0;
    // }
    // set up PTS data
    const auto& msg = msgs;

    float* framePtsData = framePts.data_ptr<float>();
    
    float pts_s = float(float(msg.header.pts) * 1e-6);
    framePtsData[0] =  pts_s;
    
    T* frameData = frame.numel() > 0 ? frame.data_ptr<T>() : nullptr;

    
    if (frameData) {
        auto sizeInBytes = msg.payload->length();
        memcpy(frameData, msg.payload->data(), sizeInBytes);
    }
  return sizeof(T);
}

size_t fillVideoTensor(
    DecoderOutputMessage& msgs,
    torch::Tensor& videoFrame,
    torch::Tensor& videoFramePts) {
  return fillTensorList<uint8_t>(msgs, videoFrame, videoFramePts);
}


std::string parse_type_to_string(const std::string& stream_string) {
  static const std::array<std::pair<std::string, MediaType>, 4> types = {{
      {"video", TYPE_VIDEO},
      {"audio", TYPE_AUDIO},
      {"subtitle", TYPE_SUBTITLE},
      {"cc", TYPE_CC},
  }};
  auto device = std::find_if(
      types.begin(),
      types.end(),
      [stream_string](const std::pair<std::string, MediaType>& p) {
        return p.first == stream_string;
      });
  if (device != types.end()) {
    return device->first;
  }
  AT_ERROR(
      "Expected one of [audio, video, subtitle, cc] ", stream_string);
}

MediaType parse_type_to_mt(const std::string& stream_string) {
  static const std::array<std::pair<std::string, MediaType>, 4> types = {{
      {"video", TYPE_VIDEO},
      {"audio", TYPE_AUDIO},
      {"subtitle", TYPE_SUBTITLE},
      {"cc", TYPE_CC},
  }};
  auto device = std::find_if(
      types.begin(),
      types.end(),
      [stream_string](const std::pair<std::string, MediaType>& p) {
        return p.first == stream_string;
      });
  if (device != types.end()) {
    return device->second;
  }
  AT_ERROR(
      "Expected one of [audio, video, subtitle, cc] ", stream_string);
}

std::tuple<std::string, int64_t> _parseStream(const std::string& streamString){
    TORCH_CHECK(!streamString.empty(), "Stream string must not be empty");
    static const std::regex regex("([a-zA-Z_]+)(?::([1-9]\\d*|0))?");
    std::smatch match;

    TORCH_CHECK(
        std::regex_match(streamString, match, regex),
        "Invalid stream string: '", streamString, "'");
    
    std::string type_ = "video";
    type_ = parse_type_to_string(match[1].str());
    int64_t index_ = -1;
    if (match[2].matched) {
        try {
        index_ = c10::stoi(match[2].str());
        } catch (const std::exception &) {
        AT_ERROR(
            "Could not parse device index '", match[2].str(),
            "' in device string '", streamString, "'");
        }
    }
    return std::make_tuple(type_, index_);
}


void Video::_getDecoderParams(
        int64_t videoStartUs,
        int64_t getPtsOnly,

        std::string stream,
        long stream_id=-1,
        bool all_streams=false,
        double seekFrameMarginUs=10){

    
    params.timeoutMs = decoderTimeoutMs;
    params.startOffset = videoStartUs;
    params.seekAccuracy = 10;
    params.headerOnly = false;

    params.preventStaleness = false;  // not sure what this is about


    if (all_streams == true){
        MediaFormat format;
        format.stream = -2;
        format.type = TYPE_AUDIO;
        params.formats.insert(format);

        format.type = TYPE_VIDEO;
        format.stream = -2;
        format.format.video.width = 0;
        format.format.video.height = 0;
        format.format.video.cropImage = 0;
        params.formats.insert(format);

        format.type = TYPE_SUBTITLE;
        format.stream = -2;
        params.formats.insert(format);

        format.type = TYPE_CC;
        format.stream = -2;
        params.formats.insert(format);
    } else{
        // parse stream type
        MediaType stream_type = parse_type_to_mt(stream);
        
        // TODO: reset params.formats
        std::set<MediaFormat> formats;
        params.formats = formats;
        // Define new format
        MediaFormat format;
        format.type = stream_type;
        format.stream = stream_id;
        if (stream_type == TYPE_VIDEO){
            format.format.video.width = 0;
            format.format.video.height = 0;
            format.format.video.cropImage = 0;
        }
        params.formats.insert(format);
    }

} // _get decoder params


Video::Video(
    std::string videoPath, 
    std::string stream, 
    bool isReadFile) {


    //parse stream information

    Video::_getDecoderParams(
        0,      // video start
        0,  //headerOnly
        get<0>(current_stream), // stream
        long(-1),     // stream_id parsed from info above change to -2
        true    // read all streams
    );

    std::string logMessage, logType;
    
    // TODO: add read from memory option
    params.uri = videoPath;
    logType = "file";
    logMessage = videoPath;
    

    cout << "Video decoding to gather metadata from " << logType << " [" << logMessage
          << "] has started \n";
    

    
    std::vector<double> audioFPS, videoFPS, ccFPS, subsFPS;
    std::vector<double> audioDuration, videoDuration, ccDuration, subsDuration;
    std::vector<double> audioTB, videoTB, ccTB, subsTB;
    

    // calback and metadata defined in struct
    succeeded = decoder.init(params, std::move(callback), &metadata);
    if (succeeded) {
        for (const auto& header : metadata) {
            double fps = double(header.fps);
            double timeBase = double(header.num) / double(header.den);
            double duration = double(header.duration) * 1e-6; // * timeBase;


            cout << "Decoding stream of" << header.format.type;
            cout << "duration " << duration << " tb" << timeBase << " " << double(header.num) << " " <<double(header.num);


            if (header.format.type == TYPE_VIDEO) {
                videoMetadata = header;
                videoFPS.push_back(fps);
                videoDuration.push_back(duration);
            } else if (header.format.type == TYPE_AUDIO) {
                audioFPS.push_back(fps);
                audioDuration.push_back(duration);
            } else if (header.format.type == TYPE_CC){
                ccFPS.push_back(fps);
                ccDuration.push_back(duration);
            } else if (header.format.type == TYPE_SUBTITLE){
                subsFPS.push_back(fps);
                subsDuration.push_back(duration);
            };
        }

    }

    streamFPS.insert({{"video", videoFPS}, {"audio", audioFPS}});
    streamDuration.insert({{"video", videoDuration}, {"audio", audioDuration}});
} //video

std::tuple<std::string, int64_t> Video::getCurrentStream() const {
    return current_stream;
}

std::vector<double> Video::getFPS(std::string stream) const{
    // add safety check
    if (stream.empty()){
        stream = get<0>(current_stream);
    }
    auto stream_tpl = _parseStream(stream);
    std::string stream_str = get<0>(stream_tpl);
    // check if the stream exists
    return streamFPS.at(stream_str);
}

std::vector<double> Video::getDuration(std::string stream) const{
    // add safety check
    if (stream.empty()){
        stream = get<0>(current_stream);
    }
    auto stream_tpl = _parseStream(stream);
    std::string stream_str = get<0>(stream_tpl);
    // check if the stream exists
    return streamDuration.at(stream_str);
}

int64_t Video::Seek(double ts, std::string stream="", bool any_frame=false){
    if (stream.empty()){
        stream = get<0>(current_stream);
    }
    auto stream_tpl = _parseStream(stream);
    // check if the stream exists

    // convert time to microseconds and cast to unsigned long int
    int64_t ts_out = int64_t(ts * 1e6);

    Video::_getDecoderParams(
        ts_out,
        0, // we're in full get frame mode
        get<0>(stream_tpl),
        get<1>(stream_tpl),
        false);
    
    bool succeeded = decoder.init(params, std::move(callback), &metadata);
    if (succeeded){
        // initialize the class variables and retrurn
        video_any_frame = any_frame;
        seekTS = ts; 
        return 0;
    }
    return 1;
}

torch::List<torch::Tensor> Video::Next(std::string stream=""){


    // first decode the frame
    DecoderOutputMessage out;
    int64_t res = decoder.decode(&out, decoderTimeoutMs);
    auto header = out.header;
    const auto& format = header.format;

    // then initialize the output variables based on type
    size_t expectedWrittenBytes = 0;
    torch::Tensor framePTS = torch::zeros({1}, torch::kFloat);

    torch::Tensor outFrame = torch::zeros({0}, torch::kByte);
    if (format.type == TYPE_VIDEO) {
        int outHeight = format.format.video.height;
        int outWidth = format.format.video.width;
        int numChannels = 3;
        outFrame = torch::zeros({outHeight, outWidth, numChannels}, torch::kByte);
        expectedWrittenBytes = outHeight * outWidth * numChannels;
        std::cout << expectedWrittenBytes;
    }
    
    // if not in seek mode or only looking at the keyframes, 
    // return the immediate next frame 
    if ((seekTS == -1) || (video_any_frame == false)) {            
        auto numberWrittenBytes = fillVideoTensor(out, outFrame, framePTS);
        out.payload.reset();
    }

    torch::List<torch::Tensor> result;
    result.push_back(outFrame);
    result.push_back(framePTS);
    return result;
}

