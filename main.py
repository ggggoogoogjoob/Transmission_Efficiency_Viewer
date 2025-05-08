import sys
import os
import nibabel as nib
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QFileDialog, QLabel, QVBoxLayout,
    QWidget, QHBoxLayout, QSlider, QGroupBox, QInputDialog, QMessageBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import pyvista as pv
from scipy.io import loadmat

class TmEViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transmission Efficiency Viewer")
        self.setGeometry(100, 100, 1200, 600)
        self.data = None
        self.init_ui()

    def init_ui(self):
        # 菜單
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        open_action = QAction('Open (.nii)', self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        function_menu = menubar.addMenu('Function')
        insertion_loss_action = QAction('Transmission Efficiency (.mat)', self)
        insertion_loss_action.triggered.connect(self.show_insertion_loss_map)
        function_menu.addAction(insertion_loss_action)

        self.statusBar().showMessage('Ready')

        self.axial_label = QLabel('Axial view')
        self.coronal_label = QLabel('Coronal view')
        self.sagittal_label = QLabel('Sagittal view')
        for label in [self.axial_label, self.coronal_label, self.sagittal_label]:
            label.setAlignment(Qt.AlignCenter)

        self.axial_slider = QSlider(Qt.Horizontal)
        self.coronal_slider = QSlider(Qt.Horizontal)
        self.sagittal_slider = QSlider(Qt.Horizontal)
        self.axial_slider.valueChanged.connect(self.update_views)
        self.coronal_slider.valueChanged.connect(self.update_views)
        self.sagittal_slider.valueChanged.connect(self.update_views)

        main_widget = QWidget()

        horizontal_layout = QHBoxLayout()  # Use QHBoxLayout for left-to-right alignment
        horizontal_layout.addWidget(
            self.create_view_box("Axial", self.axial_label, self.axial_slider))
        horizontal_layout.addWidget(
            self.create_view_box("Coronal", self.coronal_label,
                                 self.coronal_slider))
        horizontal_layout.addWidget(
            self.create_view_box("Sagittal", self.sagittal_label,
                                 self.sagittal_slider))

        main_widget.setLayout(horizontal_layout)  # Set the horizontal layout
        self.setCentralWidget(main_widget)

    def create_view_box(self, title, label, slider):
        group_box = QGroupBox(title)
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(slider)
        group_box.setLayout(layout)
        return group_box

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open NIfTI File", "", "NIfTI Files (*.nii *.nii.gz)")
        if file_path:
            self.statusBar().showMessage(f'Loading {os.path.basename(file_path)}')
            self.load_nii(file_path)

    def load_nii(self, file_path):
        try:
            nii_img = nib.load(file_path)
            self.data = nii_img.get_fdata()
            if self.data.ndim != 3:
                self.statusBar().showMessage('Only 3D images supported')
                return

            self.axial_slider.setMaximum(self.data.shape[2] - 1)
            self.axial_slider.setValue(self.data.shape[2] // 2)
            self.coronal_slider.setMaximum(self.data.shape[1] - 1)
            self.coronal_slider.setValue(self.data.shape[1] // 2)
            self.sagittal_slider.setMaximum(self.data.shape[0] - 1)
            self.sagittal_slider.setValue(self.data.shape[0] // 2)

            self.update_views()
            self.statusBar().showMessage(f"Loaded: {os.path.basename(file_path)}")
        except Exception as e:
            self.statusBar().showMessage(f"Failed to load image: {str(e)}")

    def set_slice_to_label(self, slice_img, label):
        norm_img = ((slice_img - np.min(slice_img)) / (np.ptp(slice_img) + 1e-5) * 255).astype(np.uint8)
        h, w = norm_img.shape
        qimg = QImage(norm_img.tobytes(), w, h, w, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimg).scaled(350, 350, Qt.KeepAspectRatio)
        label.setPixmap(pixmap)

    def update_views(self):
        if self.data is None:
            return
        axial_idx = self.axial_slider.value()
        coronal_idx = self.coronal_slider.value()
        sagittal_idx = self.sagittal_slider.value()
        self.set_slice_to_label(np.rot90(self.data[:, :, axial_idx]), self.axial_label)
        self.set_slice_to_label(np.rot90(self.data[:, coronal_idx, :]), self.coronal_label)
        self.set_slice_to_label(np.rot90(self.data[sagittal_idx, :, :]), self.sagittal_label)

    def show_insertion_loss_map(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Select .mat file",
                                                       "",
                                                       "MATLAB Files (*.mat)")
            if not file_path:
                return
            mat = loadmat(file_path)

            # Extract other variables
            x = np.array(mat['x4']).flatten()
            y = np.array(mat['y4']).flatten()
            z = np.array(mat['z4']).flatten()
            points = np.vstack((x, y, z)).T.astype(np.float32)

            inner_angle = np.array(mat['inner_angle']).flatten()
            outer_angle = np.array(mat['outer_angle']).flatten()

            average_angle = (inner_angle + outer_angle) / 2  # Calculate average angle

            line_density = np.array(mat['line_density_ratio_2']).flatten()
            line_density[line_density > 1] = 1.0

            line_thickness = np.array(mat['line_thickness_2']).flatten()

            insertion_loss = np.nan_to_num(
                np.array(mat['seeds_trans_efficiency']), nan=0.0)
            insertion_loss[insertion_loss > 1] = 0.0

            freq_value, ok = QInputDialog.getInt(self, "Select Frequency",
                                                 "Enter frequency (100-1000 kHz):",
                                                 value=100, min=100, max=1000,
                                                 step=10)

            if ok:
                # The frequency input is valid; now calculate the index
                if freq_value % 10 != 0:
                    QMessageBox.warning(self, "Invalid Frequency",
                                        "Frequency must be in steps of 10 kHz.")
                    return

                freq_index = (freq_value - 100) // 10

            f_insertion_loss = insertion_loss[freq_index, :]


            plotter = pv.Plotter(shape=(1, 4), window_size=(1800, 600))

            # Subplot 1: Average Angle (instead of Inner Angle and Outer Angle)
            plotter.subplot(0, 0)
            pdata = pv.PolyData(points)
            pdata['Average Angle'] = average_angle
            plotter.add_points(pdata, scalars='Average Angle', cmap='viridis',
                               point_size=5.0)
            plotter.add_text("Average Angle", font_size=6)

            # Subplot 2: Line Density Ratio
            plotter.subplot(0, 1)
            pdata = pv.PolyData(points)
            pdata['Line Density'] = line_density
            plotter.add_points(pdata, scalars='Line Density', cmap='coolwarm',
                               point_size=5.0)
            plotter.add_text("Line Density Ratio", font_size=6)

            # Subplot 3: Line Thickness
            plotter.subplot(0, 2)
            pdata = pv.PolyData(points)
            pdata['Line Thickness'] = line_thickness
            plotter.add_points(pdata, scalars='Line Thickness', cmap='cividis',
                               point_size=5.0)
            plotter.add_text("Line Thickness", font_size=6)

            # Subplot 4: Insertion Loss
            plotter.subplot(0, 3)
            pdata = pv.PolyData(points)
            pdata['Transmission Efficiency'] = f_insertion_loss
            plotter.add_points(pdata, scalars='Transmission Efficiency',
                               cmap='hot', point_size=5.0)
            plotter.add_text("Transmission Efficiency", font_size=6)
            plotter.show()

            # 更新状态栏
            self.statusBar().showMessage(
                "3D Skull Properties + Insertion Loss Displayed")


        except Exception as e:
            self.statusBar().showMessage("Failed to display")
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
            print("Error:", str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = TmEViewer()
    viewer.show()
    sys.exit(app.exec_())
