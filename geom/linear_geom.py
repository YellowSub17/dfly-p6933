import re

def offset_geometry_by_module(input_path, output_path):
    # Regex to find: p(number)a(number)/min_ss = (value)
    # Group 1: The module number
    # Group 2: The parameter name (min_ss or max_ss)
    # Group 3: The original value
    pattern = re.compile(r'p(\d+)a\d+/(min_ss|max_ss)\s*=\s*(\d+)')

    new_lines = []

    with open(input_path, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                module_num = int(match.group(1))
                param_name = match.group(2)
                original_value = int(match.group(3))
                
                # Calculate the new value: original + (512 * p)
                new_value = original_value + (512 * module_num)
                
                # Reconstruct the line (keeping the prefix)
                # We use the match start/end to preserve the line's structure
                prefix = line.split('=')[0].split('/')[0] # e.g., p0a0
                new_line = f"{prefix}/{param_name} = {new_value}\n"
                new_lines.append(new_line)
            else:
                # Keep everything else as is
                new_lines.append(line)

    with open(output_path, 'w') as f:
        f.writelines(new_lines)

    print("Success! Geometry file updated using p*512 offset.")



# def fix_exfel_indices(input_path, output_path):
#     # Regex to find the panel name and parameters
#     # We look for min_ss, max_ss, and dim1
#     pattern = re.compile(r'(p\d+a\d+)/(min_ss|max_ss|dim1)\s*=\s*(\d+|ss|fs)')

#     new_lines = []
    
#     with open(input_path, 'r') as f:
#         for line in f:
#             match = pattern.search(line)
#             if match:
#                 prefix = match.group(1)
#                 param = match.group(2)
#                 val = match.group(3)
                
#                 # If it's a min_ss or max_ss, we subtract (512 * dim1)
#                 # But since your p0 is 0-511 and p1 is 512-1023, 
#                 # a simple modulo 512 is the cleanest fix.
#                 if param in ['min_ss', 'max_ss']:
#                     corrected_val = int(val) % 512
#                     new_lines.append(f"{prefix}/{param} = {corrected_val}\n")
#                 else:
#                     # Keep dim1, dim2, dim3 etc. as they are
#                     new_lines.append(line)
#             else:
#                 new_lines.append(line)

#     with open(output_path, 'w') as f:
#         f.writelines(new_lines)

#     print("File corrected! All modules now use local 0-511 indexing.")


# Run the script
offset_geometry_by_module('./agipd_p008039_r0014.geom', 'agipd_linear.geom')

#fix_exfel_indices('agipd_linear.geom', 'agipd_linear_fix.geom')
