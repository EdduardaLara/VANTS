// Copyright 2004-present Facebook. All Rights Reserved.

#pragma once

#include "defs.h"

extern "C" {
#include <libavformat/avformat.h>
#include "libswscale/swscale.h"
}

namespace ffmpeg {

/**
 * Class transcode video frames from one format into another
 */

class VideoSampler : public MediaSampler {
 public:
  VideoSampler(
    int swsFlags = SWS_AREA,
    int64_t loggingUuid = 0);

  ~VideoSampler() override;

  // MediaSampler overrides
  bool init(const SamplerParameters& params) override;
  MediaType getMediaType() const override { return MediaType::TYPE_VIDEO; }
  FormatUnion getInputFormat() const override { return params_.in; }
  FormatUnion getOutFormat() const override { return params_.out; }
  int sample(const ByteStorage* in, ByteStorage* out) override;
  void shutdown() override;

  // returns number processed/scaling bytes
  int sample(AVFrame* frame, ByteStorage* out);
  int getImageBytes() const;
 private:
  // close resources
  void cleanUp();
  // helper functions for rescaling, cropping, etc.
  int sample(
      const uint8_t* const srcSlice[],
      int srcStride[],
      ByteStorage* out,
      bool allocateBuffer);

 private:
  SamplerParameters params_;
  VideoFormat scaleFormat_;
  SwsContext* scaleContext_{nullptr};
  SwsContext* cropContext_{nullptr};
  int swsFlags_{SWS_AREA};
  std::vector<uint8_t> scaleBuffer_;
  int64_t loggingUuid_{0};
};

}
