# Overview
This Viewer is a Python-based graphical application built with PyQt5 and PyVista. It allows users to:
**· Visualize 3D medical images (CT or MRI of the skull) stored in NIfTI format (.nii, .nii.gz), using interactive slice viewers.**

**· Load and display transmission efficiency results from paper reference() in .mat form.**


# Load .nii Medical Images
**Menu:** `File > Open (.nii)`
- Supports `.nii` and `.nii.gz` 3D image formats  
- Displays: **Axial** , **Coronal** , **Sagittal** slice views

![3D View Example](https://github.com/user-attachments/assets/ef631db0-4226-4039-a6fe-a549ebc4365d)


# Visualize Transmission Efficiency and Skull Properties
**Menu:** `Function > Transmission Efficiency (.mat)`
Load a `.mat` file containing the following variables:
- `x4`, `y4`, `z4` – 3D coordinates of each beam path point (**N×1** vectors)
- `inner_angle`, `outer_angle` – Incidence and exit angles (**N×1** vectors)
- `line_density_ratio_2` – Normalized density ratio along beam path (range **0–1**)
- `line_thickness_2` – Skull thickness along each beam path (**N×1**)
- `seeds_trans_efficiency` – Transmission efficiency at multiple frequencies (**F×N** matrix)
> **N**: Number of sampled points  
> **F**: Number of frequencies

Users are prompted to select a frequency (100–1000 kHz, in 10 kHz steps).
The tool visualizes 3D data using PyVista, with four linked subplots:
Average Angle (mean of inner and outer angles)
Line Density Ratio
Line Thickness
Transmission Efficiency at the selected frequency

![image](https://github.com/user-attachments/assets/62f8ebbd-a23f-4865-b33f-92b180fdfeb0)
