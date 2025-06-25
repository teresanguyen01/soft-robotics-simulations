#!/usr/bin/env python3
import numpy as np
import pandas as pd
import argparse

# ─── quaternion math ────────────────────────────────────────────────────────────
def quat_inverse(q):
    w, x, y, z = q
    norm2 = w*w + x*x + y*y + z*z
    return np.array([w, -x, -y, -z]) / norm2

def quat_mul(a, b):
    w1, x1, y1, z1 = a
    w2, x2, y2, z2 = b
    return np.array([
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2
    ])

def quat_to_expmap(q):
    w, x, y, z = q
    # normalize if necessary
    if abs(w) > 1.0:
        q = q / np.linalg.norm(q)
        w, x, y, z = q
    angle = 2 * np.arccos(w)
    s = np.sqrt(max(0.0, 1 - w*w))
    if s < 1e-8:
        return np.zeros(3)
    axis = np.array([x, y, z]) / s
    return axis * angle

# ─── build qpos ────────────────────────────────────────────────────────────────
def make_qpos(mocap_csv, out_csv):
    df = pd.read_csv(mocap_csv)
    n = len(df)

    # exact DOF names expected in output
    dof_names = [
        "time_ms",
        "x", "y", "z", "qw", "qx", "qy", "qz",
        "abdomen_z_0", "abdomen_z_1",
        "shoulder1_right_0", "shoulder1_right_1",
        "shoulder1_left_0", "shoulder1_left_1",
        "abdomen_x",
        "elbow_right", "elbow_left",
        "hip_x_right_0", "hip_x_right_1", "hip_x_right_2",
        "hip_x_left_0", "hip_x_left_1", "hip_x_left_2",
        "knee_right", "knee_left",
        "ankle_y_right_0", "ankle_y_right_1",
        "ankle_y_left_0", "ankle_y_left_1",
    ]

    # prepare output DataFrame
    out = pd.DataFrame(columns=dof_names)
    out["time_ms"] = df["time_ms"]

    # root translation (in mm)
    out["x"]  = df["base_X.1"]
    out["y"]  = df["base_Y.1"]
    out["z"]  = df["base_Z.1"]
    out["qw"] = df["base_W"]
    out["qx"] = df["base_X"]
    out["qy"] = df["base_Y"]
    out["qz"] = df["base_Z"]

    # planar joints (positions in mm)
    def plan(col_name, child, parent, axis):
        out[col_name] = df[f"{child}_{axis}.1"] - df[f"{parent}_{axis}.1"]

    plan("abdomen_z_0", "abdomen",      "base",       "X")
    plan("abdomen_z_1", "abdomen",      "base",       "Y")
    plan("shoulder1_right_0", "right_shoulder", "abdomen", "X")
    plan("shoulder1_right_1", "right_shoulder", "abdomen", "Y")
    plan("shoulder1_left_0",  "left_shoulder",  "abdomen", "X")
    plan("shoulder1_left_1",  "left_shoulder",  "abdomen", "Y")
    plan("ankle_y_right_0",   "right_ankle",    "right_knee", "X")
    plan("ankle_y_right_1",   "right_ankle",    "right_knee", "Y")
    plan("ankle_y_left_0",    "left_ankle",     "left_knee",  "X")
    plan("ankle_y_left_1",    "left_ankle",     "left_knee",  "Y")

    # ── revolute & knee: compute raw values ───────────────────────────────────────
    def revolute_raw(col_name, child_seg, parent_seg, axis_vec):
        vals = np.zeros(n)
        qc = df[[f"{child_seg}_W", f"{child_seg}_X", f"{child_seg}_Y", f"{child_seg}_Z"]].values
        qp = df[[f"{parent_seg}_W", f"{parent_seg}_X", f"{parent_seg}_Y", f"{parent_seg}_Z"]].values
        for i in range(n):
            qrel = quat_mul(quat_inverse(qp[i]), qc[i])
            v    = quat_to_expmap(qrel)
            vals[i] = np.dot(v, axis_vec)
        out[col_name] = vals

    def knee_raw(col_name, hip, kne, ank):
        hip_p = df[[f"{hip}_X.1", f"{hip}_Y.1", f"{hip}_Z.1"]].values
        kne_p = df[[f"{kne}_X.1", f"{kne}_Y.1", f"{kne}_Z.1"]].values
        ank_p = df[[f"{ank}_X.1", f"{ank}_Y.1", f"{ank}_Z.1"]].values
        dots = np.sum((hip_p - kne_p) * (ank_p - kne_p), axis=1)
        n1   = np.linalg.norm(hip_p - kne_p, axis=1)
        n2   = np.linalg.norm(ank_p - kne_p, axis=1)
        cosang = np.clip(dots / (n1 * n2), -1.0, 1.0)
        out[col_name] = np.arccos(cosang)

    # compute raw joint values
    revolute_raw("abdomen_x_raw",   "abdomen",       "base",            np.array([1,0,0]))
    revolute_raw("elbow_right_raw", "right_forearm", "right_upper_arm", np.array([-1,0,0]))
    revolute_raw("elbow_left_raw",  "left_forearm",  "left_upper_arm",  np.array([1,0,0]))
    knee_raw("knee_right_raw", "right_thigh", "right_knee", "right_ankle")
    knee_raw("knee_left_raw",  "left_thigh",  "left_knee",  "left_ankle")

    # ── correct sign & zero-offset per joint ─────────────────────────────────────
    # abdomen_x: subtract initial offset
    data = out["abdomen_x_raw"].values
    out["abdomen_x"] = data - data[0]
    del out["abdomen_x_raw"]

    # elbows: zero at first frame (axisVec sign correct already)
    for name in ["elbow_right", "elbow_left"]:
        raw = name + "_raw"
        vals = out[raw].values
        out[name] = vals - vals[0]
        del out[raw]

    # knees: zero at first frame
    for name in ["knee_right", "knee_left"]:
        raw = name + "_raw"
        vals = out[raw].values
        out[name] = vals - vals[0]
        del out[raw]

    # ── spherical joints (exp-map) ────────────────────────────────────────────────
    def spherical(start, child, parent):
        expm = np.zeros((n,3))
        qc = df[[f"{child}_W", f"{child}_X", f"{child}_Y", f"{child}_Z"]].values
        qp = df[[f"{parent}_W",f"{parent}_X",f"{parent}_Y",f"{parent}_Z"]].values
        for i in range(n):
            qrel = quat_mul(quat_inverse(qp[i]), qc[i])
            expm[i] = quat_to_expmap(qrel)
        out[f"{start}_0"] = expm[:,0]
        out[f"{start}_1"] = expm[:,1]
        out[f"{start}_2"] = expm[:,2]

    spherical("hip_x_right", "right_thigh", "base")
    spherical("hip_x_left",  "left_thigh",  "base")

    # ── convert mm→m for all positional DOFs ─────────────────────────────────────
    linear = [
        "x","y","z",
        "abdomen_z_0","abdomen_z_1",
        "shoulder1_right_0","shoulder1_right_1",
        "shoulder1_left_0","shoulder1_left_1",
        "ankle_y_right_0","ankle_y_right_1",
        "ankle_y_left_0","ankle_y_left_1",
    ]
    out[linear] = out[linear] / 1000.0

    # ── write out ────────────────────────────────────────────────────────────────
    out.to_csv(out_csv, index=False)
    print(f"Wrote {n} frames → {out_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build a MuJoCo‐style qpos CSV with corrected joint axes"
    )
    parser.add_argument('--mocap', required=True, help="input mocap CSV")
    parser.add_argument('--out',   required=True, help="output qpos CSV")
    args = parser.parse_args()
    make_qpos(args.mocap, args.out)