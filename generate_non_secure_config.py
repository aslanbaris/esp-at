import os

def disable_security(config_path, output_path):
    with open(config_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    keys_to_disable = [
        "CONFIG_SECURE_BOOT",
        "CONFIG_SECURE_BOOT_V2_ENABLED",
        "CONFIG_SECURE_BOOT_BUILD_SIGNED_BINARIES",
        "CONFIG_SECURE_SIGNED_ON_BOOT",
        "CONFIG_SECURE_FLASH_ENC_ENABLED",
        "CONFIG_FLASH_ENCRYPTION_ENABLED",
        "CONFIG_SECURE_BOOT_V2_RSA_ENABLED",
    ]

    for line in lines:
        line = line.strip()
        if not line:
            new_lines.append(line)
            continue
        
        is_security_config = False
        for key in keys_to_disable:
            if line.startswith(f"{key}=y"):
                new_lines.append(f"# {key} is not set")
                is_security_config = True
                break
            # Handle string configs if any (e.g. key path)
            if line.startswith(f'{key}=') and key == "CONFIG_SECURE_BOOT_SIGNING_KEY":
                 new_lines.append(f"# {key} is not set")
                 is_security_config = True
                 break

        if not is_security_config:
            new_lines.append(line)

    with open(output_path, 'w') as f:
        for line in new_lines:
            f.write(line + '\n')
    
    print(f"Generated {output_path}")

if __name__ == "__main__":
    disable_security("sdkconfig.security_enabled", "sdkconfig.security_disabled")
