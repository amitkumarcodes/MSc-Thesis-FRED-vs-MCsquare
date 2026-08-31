import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt

# -----------------------------
# Phantom settings
# -----------------------------
N = 200              # 200 x 200 x 200 voxels
spacing = 1.0           # mm
L = N * spacing         # total size = 200 mm

HU_WATER = 0

# -----------------------------
# Create CT phantom
# -----------------------------
ct = np.full((N, N, N), HU_WATER, dtype=np.int16)

# -----------------------------
# Write images
# -----------------------------
def write_mha(array_zyx, filename):
    img = sitk.GetImageFromArray(array_zyx)
    img.SetSpacing((spacing, spacing, spacing))
    img.SetOrigin((spacing / 2, spacing / 2, spacing / 2))
    sitk.WriteImage(img, str(filename))

write_mha(ct, "CT_HU_200mm_water.mha")

# -----------------------------
# Visual check
# -----------------------------
x_index = N // 2
slice_yz = ct[:, :, x_index]

plt.figure(figsize=(6, 5))
plt.imshow(
    slice_yz,
    origin="lower",
    extent=[0, L, 0, L],
    aspect="equal"
)
plt.xlabel("y [mm]")
plt.ylabel("z [mm]")
plt.title("Central x-slice: y-z plane")
plt.colorbar(label="HU")
plt.tight_layout()
plt.savefig("phantom_check_yz_slice_200mm.png", dpi=200)
plt.show()

# -----------------------------
# Sanity checks
# -----------------------------
print("Phantom created successfully.")
print(f"CT shape [z, y, x] = {ct.shape}")
print(f"Spacing = {spacing} mm")
print()
print("Voxel counts:")
print(f"Water HU=0:      {np.sum(ct == HU_WATER)}")
print()
print("Files saved:")
print("CT_HU_200mm_water.mha")
print("phantom_check_yz_slice_200mm.png")
