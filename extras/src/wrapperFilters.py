
import cv2  ## 4.12.0 or above
import numpy as np

### ----------------------- Filters ------------------------                                                                                                                                                                                                                                                                           
class Filters: 
### -------------------------------------------------------- 
    def __init__(self, parent):
        super().__init__()
             
        self.parent = parent
        self.sliders = parent.sliders
        
### --------------------------------------------------------     
    '''        --- FILTER 8: ACTIVE SEAM CONTROL ---
    A compositing tool designed to blend overlapping images without "ghosting" 
    or washing out the main subjects. It searches for foreground elements (like dark 
    trees or stones) and locks them in at full opacity.  The result, sharpen
    subjects that appear cleanly rendered while the surrounding environment 
    seamlessly melts together behind them.  
    Googles' words not mine. ''' 
### -------------------------------------------------------- 
    def Filter8(self, strip1, strip2):
        self.sliders.filter8Btn.setText("Filter 8 On") 
        h, w, _ = strip1.shape

        ''' bottom Lock: Uses luminance to isolate and preserve 
            specific dark textures (stones/architecture) at 100% opacity. 
        '''
        gray1 = cv2.cvtColor(strip1, cv2.COLOR_BGR2GRAY)
        
        target_val = int((self.parent.bottomValue/ 100.0) * 255)
        
        # Keep threshold tight around the target darkness
        lower_clamp = max(0, target_val - 25)
        upper_clamp = min(255, target_val + 25)
        stone_mask = cv2.inRange(gray1, lower_clamp, upper_clamp)
        
        # Give the stone mask a light, fixed edge-softening
        stone_mask = cv2.GaussianBlur(stone_mask, (11,11), 0)  ## changed  was 7,7
        fg_weight = stone_mask.astype(np.float32) / 255.0

        ''' topEnd Seam Melter: Uses an adjustable S-Curve (tanh) to create
            a smooth, responsive crossfade across the rest of the topEnd. 
        '''
        # Pull slider percentage (0.01 to 1.0)
        seam_softness = max(0.01, float(self.parent.topEndValue ) / 100.0)
        
        # Create a base linear ramp across the width (0.0 to 1.0)
        x = np.linspace(0.0, 1.0, w, dtype=np.float32)
        
        # Apply an S-Curve (Smoothstep) weighted by Slider 2
        # When softness is high, it creates a wide, gentle crossfade across the field.
        # When softness is low, it tightens the blend zone.
        center = 0.5
        ramp = 0.5 - 0.5 * np.tanh((x - center) / (seam_softness * 0.5))
        ramp = np.tile(ramp, (h, 1))

        ''' Master Blend: Prioritizes the solid bottom mask, then fills 
            the remaining area using the smooth topEnd gradient. 
        '''
        # If stone is detected (fg_weight), keep Left Image solid.
        # Otherwise, route through our responsive S-Curve ramp!
        master_alpha = fg_weight + (1.0 - fg_weight) * ramp
        master_alpha = np.clip(master_alpha, 0.0, 1.0)
        master_alpha = np.stack([master_alpha, master_alpha, master_alpha], axis=2)

        # --- DIRECT NATIVE RGB/BGR BLEND ---
        s1_float = strip1.astype(np.float32)
        s2_float = strip2.astype(np.float32)
        
        return np.clip(s1_float * master_alpha + s2_float * (1.0 - master_alpha), 0, 255).astype(np.uint8)
   
### ------------------------------------------------------- 
    '''               --- 9. Spatial Fuzziness ---
    A soft-edge compositing tool designed to handle complex, scattered textures 
    (like leaves, grass, or branches) without creating jagged, noisy pixel artifacts.  
    It pre-groups similar pixels together, isolates the target shadows, and then 
    physically expands the mask to create a feathered "halo" around fine details.  
    The results, high-frequency subjects are preserved and blended smoothly into 
    the background gradient without looking artificially cut out or stamped.
    Googles' words not mine.'''
### -------------------------------------------------------- 
    def Filter9(self, strip1, strip2):
        self.sliders.filter9Btn.setText("Filter 9 On") 
        h, w, _ = strip1.shape
        
        # 1A. Convert to grayscale
        gray1 = cv2.cvtColor(strip1, cv2.COLOR_BGR2GRAY)

        # 1B. PRE-BLUR (Spatial Fuzziness Part 1):
        # A 5x5 blur forces each pixel to average with neighbors within a 2-pixel radius
        # before thresholding, eliminating isolated pixel dropouts.
        gray_fuzzy = cv2.GaussianBlur(gray1, (5, 5), 0)
        
        '''          --- bottom THRESHOLD GATEKEEPER ---         '''
        target_val = int((self.parent.bottomValue  / 100.0) * 255)
        
        lower_clamp = max(0, target_val - 30)
        upper_clamp = min(255, target_val + 30)
        raw_mask = cv2.inRange(gray_fuzzy, lower_clamp, upper_clamp)

        # 1D. MORPHOLOGICAL DILATION (Spatial Fuzziness Part 2):
        # Literally expands any selected area outward by a 3-pixel radius (7x7 kernel)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
        stone_mask = cv2.dilate(raw_mask, kernel, iterations=1)
        
        # Smooth the expanded mask edge
        stone_mask = cv2.GaussianBlur(stone_mask, (9, 9), 0)
        fg_weight = stone_mask.astype(np.float32) / 255.0

        ''' --- topEndSlider ACTIVE BACKGROUND SEAM MELTER - blend slider) --- '''
        seam_softness = max(0.01, float(self.parent.topEndValue) / 100)
     
        x = np.linspace(0.0, 1.0, w, dtype=np.float32)
        center = 0.5
        ramp = 0.5 - 0.5 * np.tanh((x - center) / (seam_softness * 0.5))
        ramp = np.tile(ramp, (h, 1))

        # --- MASTER ALPHA ROUTING ---
        master_alpha = fg_weight + (1.0 - fg_weight) * ramp
        master_alpha = np.clip(master_alpha, 0.0, 1.0)
        master_alpha = np.stack([master_alpha, master_alpha, master_alpha], axis=2)

        # --- DIRECT NATIVE BLEND ---
        s1_float = strip1.astype(np.float32)
        s2_float = strip2.astype(np.float32)
        
        return np.clip(s1_float * master_alpha + s2_float * (1.0 - master_alpha), \
                0, 255).astype(np.uint8)
 
 ### -------------------------------------------------------- 
    '''        --- EDGE WORK: DYNAMIC SEAM FEATHERING ---
    A universal edge-cleanup utility designed to eliminate harsh vertical cut-lines 
    where the processed blend strip meets the unedited main canvas. It calculates a 
    safe blending radius based on the strip's width, then uses linear gradients to 
    crossfade the extreme left and right edge of the composite back into the pure, 
    original source pixels. Result, a seamless, artifact-free transition that anchors 
    the heavily edited blend zone smoothly into the surrounding photograph, 
    regardless of which primary filter was used.
    '''
 ### -------------------------------------------------------- 
    def EdgesSlider(self, edgeValue, blended, strip1, strip2):         
        h, w_blend, _ = blended.shape    
        max_safe_radius = w_blend // 2
        
        # Map the 1-100 slider to a percentage of that maximum safe distance
        # 100 on the slider = feather reaches the center.
        # 10 on the slider = tight, narrow edge feather.
        feather_radius = max(1, int((edgeValue / 100.0) * max_safe_radius))

        # --- LEFT SEAM FEATHER ---
        # Fades from 0.0 (100% Left Image) to 1.0 (100% Blended Math)
        ramp_left = np.linspace(0.0, 1.0, feather_radius, dtype=np.float32)
        ramp_left = np.tile(ramp_left, (h, 1))
        ramp_left = np.stack([ramp_left]*3, axis=2)
        
        s1_edge = strip1[:, 0:feather_radius].astype(np.float32)
        blend_l_edge = blended[:, 0:feather_radius].astype(np.float32)
        
        # Mix Left Original + Blended Strip
        blended[:, 0:feather_radius] = (s1_edge * (1.0 - ramp_left) + blend_l_edge * ramp_left).astype(np.uint8)

        # --- RIGHT SEAM FEATHER ---
        # Fades from 1.0 (100% Blended Math) to 0.0 (100% Right Image)
        ramp_right = np.linspace(1.0, 0.0, feather_radius, dtype=np.float32)
        ramp_right = np.tile(ramp_right, (h, 1))
        ramp_right = np.stack([ramp_right]*3, axis=2)
        
        s2_edge = strip2[:, w_blend-feather_radius : w_blend].astype(np.float32)
        blend_r_edge = blended[:, w_blend-feather_radius : w_blend].astype(np.float32)
        
        # Mix Blended Strip + Right Original
        blended[:, w_blend-feather_radius : w_blend] = (blend_r_edge * ramp_right + s2_edge * (1.0 - ramp_right)).astype(np.uint8)

        return blended
                         
### --------------------- that's all -----------------------



