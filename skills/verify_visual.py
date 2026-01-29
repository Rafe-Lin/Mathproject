
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import math
import random

def generate_triangle_image(angle_A, angle_B, angle_C):
    fig, ax = plt.subplots(figsize=(6, 6), dpi=300)

    # Calculate coordinates for the triangle
    BC_length = 5.0
    B = np.array([0.0, 0.0])
    C = np.array([BC_length, 0.0])

    angle_B_rad = math.radians(angle_B)
    angle_C_exterior_rad = math.radians(180 - angle_C)

    if abs(math.cos(angle_B_rad)) < 1e-9:
        x_A = B[0]
        y_A = BC_length / math.tan(angle_C_exterior_rad)
    elif abs(math.cos(angle_C_exterior_rad)) < 1e-9:
        x_A = C[0]
        y_A = BC_length * math.tan(angle_B_rad)
    else:
        tan_B = math.tan(angle_B_rad)
        tan_C_ext = math.tan(angle_C_exterior_rad)
        x_A = (-tan_C_ext * BC_length) / (tan_B - tan_C_ext)
        y_A = tan_B * x_A

    A = np.array([x_A, y_A])
    if A[1] < 0: A[1] = -A[1]

    vertices = np.array([A, B, C])

    # Plot Triangle
    triangle_points = np.vstack((vertices, vertices[0]))
    ax.plot(triangle_points[:, 0], triangle_points[:, 1], 'k-', lw=2)
    ax.plot(vertices[:,0], vertices[:,1], 'ko', ms=5)

    # --- helper: Centroid & Inner Position ---
    centroid = (A + B + C) / 3.0

    def get_inner_pos(vertex, center, dist=0.7):
        direction = center - vertex
        length = np.linalg.norm(direction)
        if length == 0: return vertex
        return vertex + (direction / length) * dist

    # --- helper: Angle Arcs ---
    def draw_angle_arc(ax, vertex, p1, p2, radius=0.6, color='black'):
        v_p1 = p1 - vertex
        v_p2 = p2 - vertex
        
        theta1 = np.degrees(np.arctan2(v_p1[1], v_p1[0]))
        theta2 = np.degrees(np.arctan2(v_p2[1], v_p2[0]))
        
        if theta1 < 0: theta1 += 360
        if theta2 < 0: theta2 += 360
        
        t_min, t_max = min(theta1, theta2), max(theta1, theta2)
        
        if abs(t_max - t_min) > 180:
            wedge = patches.Wedge(vertex, radius, t_max, t_min + 360, width=0.04, color=color, alpha=0.3)
        else:
            wedge = patches.Wedge(vertex, radius, t_min, t_max, width=0.04, color=color, alpha=0.3)
        
        ax.add_patch(wedge)

    # Draw Arcs
    draw_angle_arc(ax, A, B, C, radius=0.8, color='blue')
    draw_angle_arc(ax, B, A, C, radius=0.8, color='blue')
    draw_angle_arc(ax, C, A, B, radius=0.8, color='red')

    # --- Label Vertices ---
    def get_outer_pos(vertex, center, dist=0.4):
        direction = vertex - center
        length = np.linalg.norm(direction)
        return vertex + (direction / length) * dist
    
    pos_A_lbl = get_outer_pos(A, centroid, 0.4)
    pos_B_lbl = get_outer_pos(B, centroid, 0.4)
    pos_C_lbl = get_outer_pos(C, centroid, 0.4)

    ax.text(pos_A_lbl[0], pos_A_lbl[1], 'A', ha='center', va='center', fontsize=14, fontweight='bold',
           bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=0.2))
    ax.text(pos_B_lbl[0], pos_B_lbl[1], 'B', ha='center', va='center', fontsize=14, fontweight='bold',
           bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=0.2))
    ax.text(pos_C_lbl[0], pos_C_lbl[1], 'C', ha='center', va='center', fontsize=14, fontweight='bold',
           bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=0.2))

    # --- Label Angles ---
    pos_A_val = get_inner_pos(A, centroid, 1.2)
    pos_B_val = get_inner_pos(B, centroid, 1.2)
    pos_C_val = get_inner_pos(C, centroid, 1.2)

    ax.text(pos_A_val[0], pos_A_val[1], f"{angle_A}$\\degree$", ha='center', va='center', fontsize=11, color='blue')
    ax.text(pos_B_val[0], pos_B_val[1], f"{angle_B}$\\degree$", ha='center', va='center', fontsize=11, color='blue')
    ax.text(pos_C_val[0], pos_C_val[1], "?", ha='center', va='center', fontsize=14, fontweight='bold', color='red')

    # Set Limits
    ax.set_aspect('equal')
    all_x = [v[0] for v in vertices] + [pos_A_lbl[0], pos_B_lbl[0], pos_C_lbl[0]]
    all_y = [v[1] for v in vertices] + [pos_A_lbl[1], pos_B_lbl[1], pos_C_lbl[1]]
    
    pad = 1.0
    ax.set_xlim(min(all_x) - pad, max(all_x) + pad)
    ax.set_ylim(min(all_y) - pad, max(all_y) + pad)

    ax.axis('off')

    plt.savefig("verify_triangle.png", format='png', bbox_inches='tight', dpi=150)
    print("Generated verify_triangle.png")

if __name__ == "__main__":
    generate_triangle_image(40, 60, 80)
