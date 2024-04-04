# SmartWorkZoneControl-MassDOT

### Analyzing Highway Work Zone Traffic Dynamics via Thermal Videos and Deep Learning

Zubin Bhuyan, Yuanchang Xie, Ruifeng Liu, Yu Cao, Benyuan Liu

> This research project aims to develop methods to extract vehicle trajectories, use the trajectories to analyze driver behavior, particularly lane-changing behavior under different conditions, and identify safety hazards and opportunities to improve work zone safety and operations. (MassDOT Research Program with funding from FHWA SPR funds.)
>
> https://www.mass.gov/doc/smart-work-zone-control-and-performance-evaluation-based-on-trajectory-data


<table>
  <tr>
    <td> <img src="images/gif/Med-op-veh-Medford-2-COMP.gif"  alt="Andover-close call" ></td>
    <td> <img src="images/gif/Med-op-lane-Medford-2-COMP.gif" alt="Auburn-speed of vehicles" ></td>
   </tr> 
   <tr>
      <td><i>Medford, MA: Vehicle segmentation.</i></td>
      <td><i>Medford, MA: Roadway segmentation.</i> </td>
  </tr>
  <tr>
    <td> <img src="images/gif/Dan-op-veh-Danvers-2-COMP.gif"  alt="Andover-close call" ></td>
    <td> <img src="images/gif/Dan-op-lane-Danvers-2-COMP.gif" alt="Auburn-speed of vehicles" ></td>
   </tr> 
   <tr>
      <td><i>Danvers, MA: Vehicle segmentation.</i></td>
      <td><i>Danvers, MA:  Roadway segmentation.</i></td>
  </tr>
</table>

Deep learning excels in object detection due to its effective feature recognition capabilities, independent of color information. When integrated with thermal imaging, which detects heat emissions rather than relying on visible light, this approach ensures superior performance under conditions where optical cameras are ineffective.The success of deep learning applications heavily relies on a high-quality, diverse training dataset. Therefore, a substantial effort went into developing a detailed thermal vehicle dataset, designed for the specific conditions of highway work zones. This dataset, critical for training our models to perform effectively in real-world scenarios, was created from thermal footage collected in Medford and Danvers. The dataset categorizes vehicles into three classes: small, medium, and large. Small vehicles consist of sedans, motorbikes, SUVs, and pickups. Medium vehicles cover trucks like garbage and concrete mixers, construction vehicles, and buses. Large vehicles include tractor-trailers.

Video Processing Framework Highlights:

1. **Model Deployment**: The trained model and tracking module were deployed on two separate computing environments with NVIDIA A100 and RTX 4090 GPUs, enabling parallel video processing of Medford and Danvers locations.

2. **Thermal Video Inference**: Conducted frame-by-frame vehicle detection and tracking on thermal videos, leveraging powerful hardware for near real-time processing.

3. **Output Postprocessing**: Aggregated detection and tracking data per video, compiling results into a structured JSON format for easy analysis and integration with analytical tools.

4. **Video Compression**: Utilized ffmpeg to compress processed videos for efficient storage and sharing. Achieved a compression ratio of ~95%, reducing 1-hour videos from 3.5-4 GB to 60-110 MB.

Equipment

Video data table

Occluded vehicles

Trajectory analysis

Near work zone

Medford

Danvers

Campton

(link to campton)
