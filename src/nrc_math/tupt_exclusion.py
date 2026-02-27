import torch

TUPT_MOD = 2187  # 3^7
TUPT_PATTERN = [3, 6, 9, 7]

def tupt_base_check(x: torch.Tensor) -> torch.BoolTensor:
    """
    Verifies if a value falls into the 3-6-9-7 mod 2187 forbidden set.
    """
    mod_val = torch.fmod(torch.abs(x), TUPT_MOD)

    # Create exclusion mask matching multiples of 3, 6, 9, 7
    mask_3 = torch.fmod(mod_val, 3) == 0
    mask_6 = torch.fmod(mod_val, 6) == 0
    mask_9 = torch.fmod(mod_val, 9) == 0
    mask_7 = torch.fmod(mod_val, 7) == 0

    return mask_3 | mask_6 | mask_9 | mask_7

def apply_exclusion_gate(tensor: torch.Tensor) -> torch.Tensor:
    """
    Applies the Mod 2187 exclusion block. If a value falls in the forbidden
    TUPT pattern, it is gated/blocks the flow (set to 0.0).
    """
    mask = tupt_base_check(tensor)
    return tensor.masked_fill(mask, 0.0)
