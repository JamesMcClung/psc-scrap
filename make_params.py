import os
import itertools

maxwellian = False
v_coef = 1

B_vals = [0.25]
res_vals = [128]
nicells = [100, 400, 1600]
date = "nov9"  # change me

###################


def get_file_name(B: float, res: int, nicell: int) -> str:
    case_prefix = "max" if maxwellian else "exact"
    maybe_rev = "-rev" if v_coef < 0 else ""
    maybe_nicell = f"-nicell{nicell}" if nicell != 100 else ""
    return f"/mnt/lustre/IAM851/jm1667/psc-runs/case1/params/{case_prefix}{maybe_rev}/{date}/B{B:05.2f}-n{res}{maybe_nicell}.txt"


for B, res, nicell in itertools.product(B_vals, res_vals, nicells):
    dest_file = get_file_name(B, res, nicell)
    text = f"""
# Don't touch
m_i 1e9
q_i 1
n_i 1

m_e 1
q_e -1

ion false
T_i 1e-12

# Do touch
path_to_data /mnt/lustre/IAM851/jm1667/psc-scrap/inputs/case1-B={B}-input.txt

H_x {B}
rel_box_size 1

n_grid {res}
n_cells_per_patch 16

nicell {100}
cfl .75
maxwellian {str(maxwellian).lower()}

rel_box_size_3 1
n_grid_3 1

reverse_v_half false
v_e_coef {v_coef}

T_e_coef 1

# Also touch (for PscParams)
nmax 1000000
stats_every 100

fields_every 1000
moments_every 1000
gauss_every 50
particles_every 1000

checkpoint_every 500000
read_checkpoint false
# path_to_checkpoint /mnt/lustre/IAM851/jm1667/psc-runs/case1/trials/B0.1_n512_v+/checkpoint_600000.bp 
"""

    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
    with open(dest_file, "w") as file:
        print(f"Writing to {dest_file}")
        file.write(text)
