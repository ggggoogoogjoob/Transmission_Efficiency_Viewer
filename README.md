Transmission Efficiency Viewer (TmEViewer)
概述
TmEViewer 是一個用 Python (PyQt5 + PyVista) 開發的圖形化應用程式，旨在協助用戶：

查看頭骨 CT 或 MRI 的 NIfTI 檔案 (.nii / .nii.gz)，以切片形式展示 Axial、Coronal、Sagittal 三視圖。

加載和可視化透聲效率 (Transmission Efficiency) 的計算結果，以三維點雲圖方式呈現頭骨特性與聲波傳輸效率。

功能介紹
📂 打開 NIfTI 文件
點選選單：File > Open (.nii)

支援 .nii 或 .nii.gz 格式的3D醫學影像。

將影像切片顯示為三個視角：

Axial (軸向)

Coronal (冠狀)

Sagittal (矢狀)

透過滑桿快速瀏覽不同切片。

📊 Transmission Efficiency & Skull Properties 3D 顯示
點選選單：Function > Insertion Loss Map (.mat)

加載 .mat 文件（通常來自仿真或預測模型輸出）。

使用者需輸入頻率（100 ~ 1000 kHz，步進10 kHz），系統會擷取相應頻率下的透聲效率資料。

PyVista 視覺化視窗中同時呈現四張 3D 點雲圖：

Average Angle：平均傳輸角度

Line Density Ratio：線密度比

Line Thickness：厚度

Transmission Efficiency：選定頻率下的聲波效率

📁 .mat File Requirements
To enable 3D visualization of skull transmission properties and efficiency, the .mat file should include the following variables:

x4, y4, z4 – Coordinates of each transmission path point in 3D space.

inner_angle, outer_angle – Angles representing beam incidence and exit relative to skull surface.

line_density_ratio_2 – Normalized density ratio along the path (values typically between 0 and 1).

line_thickness_2 – Thickness of the skull along each path.

seeds_trans_efficiency – A 2D matrix representing transmission efficiency values across multiple frequencies (e.g., 91 frequencies × N paths).

target_point (optional) – A 3-element vector indicating the focus or target position [x, y, z].

skull_map – The original or registered 3D skull volume (e.g., CT or MRI data) used for analysis.

skull_volume – A (possibly cropped or processed) 3D volume used for display or comparison purposes.

All variables should be numerical (typically of type double) and aligned in terms of dimensionality (e.g., all path-related vectors must have the same number of entries).
