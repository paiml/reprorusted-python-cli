#!/usr/bin/env python3
"""PCA CLI - flat structure for depyler compatibility.

Simple 2D PCA on 4 data points.
"""

import argparse


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="PCA CLI")
    parser.add_argument(
        "--mode", type=str, required=True, choices=["transform", "variance"], help="Mode"
    )
    # 4 2D data points (x, y pairs)
    parser.add_argument("--x0", type=float, default=1.0, help="Point 0 x")
    parser.add_argument("--y0", type=float, default=2.0, help="Point 0 y")
    parser.add_argument("--x1", type=float, default=2.0, help="Point 1 x")
    parser.add_argument("--y1", type=float, default=3.0, help="Point 1 y")
    parser.add_argument("--x2", type=float, default=3.0, help="Point 2 x")
    parser.add_argument("--y2", type=float, default=4.0, help="Point 2 y")
    parser.add_argument("--x3", type=float, default=4.0, help="Point 3 x")
    parser.add_argument("--y3", type=float, default=5.0, help="Point 3 y")

    args = parser.parse_args()

    x0 = args.x0
    y0 = args.y0
    x1 = args.x1
    y1 = args.y1
    x2 = args.x2
    y2 = args.y2
    x3 = args.x3
    y3 = args.y3

    # Center the data
    mean_x = (x0 + x1 + x2 + x3) / 4.0
    mean_y = (y0 + y1 + y2 + y3) / 4.0

    cx0 = x0 - mean_x
    cy0 = y0 - mean_y
    cx1 = x1 - mean_x
    cy1 = y1 - mean_y
    cx2 = x2 - mean_x
    cy2 = y2 - mean_y
    cx3 = x3 - mean_x
    cy3 = y3 - mean_y

    # Covariance matrix (2x2)
    # cov_xx = sum(cx^2) / n
    # cov_xy = sum(cx*cy) / n
    # cov_yy = sum(cy^2) / n
    cov_xx = (cx0 * cx0 + cx1 * cx1 + cx2 * cx2 + cx3 * cx3) / 4.0
    cov_xy = (cx0 * cy0 + cx1 * cy1 + cx2 * cy2 + cx3 * cy3) / 4.0
    cov_yy = (cy0 * cy0 + cy1 * cy1 + cy2 * cy2 + cy3 * cy3) / 4.0

    # Eigenvalues of 2x2 symmetric matrix:
    # trace = cov_xx + cov_yy
    # det = cov_xx * cov_yy - cov_xy * cov_xy
    # eigenvalues = (trace +- sqrt(trace^2 - 4*det)) / 2
    trace = cov_xx + cov_yy
    det = cov_xx * cov_yy - cov_xy * cov_xy
    disc = trace * trace - 4.0 * det

    # Simple sqrt approximation via Newton-Raphson
    sqrt_disc = disc
    if disc > 0.0:
        sqrt_disc = disc / 2.0
        i = 0.0
        while i < 10.0:
            sqrt_disc = (sqrt_disc + disc / sqrt_disc) / 2.0
            i = i + 1.0

    lambda1 = (trace + sqrt_disc) / 2.0
    lambda2 = (trace - sqrt_disc) / 2.0

    # Total variance
    total_var = lambda1 + lambda2

    if args.mode == "transform":
        # Project onto first principal component
        # For simplicity, use the direction (1, 1) normalized
        # PC1 direction approximation
        if cov_xy > 0.0001:
            pc1_x = cov_xy
            pc1_y = lambda1 - cov_xx
        else:
            pc1_x = 1.0
            pc1_y = 0.0

        # Normalize
        mag = pc1_x * pc1_x + pc1_y * pc1_y
        mag_sqrt = mag / 2.0
        j = 0.0
        while j < 10.0:
            mag_sqrt = (mag_sqrt + mag / mag_sqrt) / 2.0
            j = j + 1.0
        if mag_sqrt > 0.0:
            pc1_x = pc1_x / mag_sqrt
            pc1_y = pc1_y / mag_sqrt

        # Project
        proj0 = cx0 * pc1_x + cy0 * pc1_y
        proj1 = cx1 * pc1_x + cy1 * pc1_y
        proj2 = cx2 * pc1_x + cy2 * pc1_y
        proj3 = cx3 * pc1_x + cy3 * pc1_y

        print(f"proj0={proj0} proj1={proj1} proj2={proj2} proj3={proj3}")
    elif args.mode == "variance":
        # Output explained variance ratio
        if total_var > 0.0:
            var_ratio1 = lambda1 / total_var
            var_ratio2 = lambda2 / total_var
        else:
            var_ratio1 = 0.0
            var_ratio2 = 0.0
        print(f"var_ratio1={var_ratio1} var_ratio2={var_ratio2}")


if __name__ == "__main__":
    main()
