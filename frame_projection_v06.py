# -*- coding: utf-8 -*-
"""A18 single-plane perspective projection: ONE 3x3 H for the entire exhibition.
No hard-coded output inner_quad and no per-material geometry.
"""
import cv2, numpy as np, math
from PIL import Image

def quad(x):
    x=np.asarray(x,dtype=np.float32)
    if x.shape!=(4,2) or abs(float(cv2.contourArea(x)))<2:
        raise ValueError("nondegenerate 4-corner quadrilateral needed")
    return x

def compute_H(source_outer,target_outer):
    h=cv2.getPerspectiveTransform(quad(source_outer),quad(target_outer))
    if abs(float(np.linalg.det(h)))<1e-9: raise ValueError("singular homography")
    return h

def derived_inner(H,source_inner):
    return cv2.perspectiveTransform(quad(source_inner).reshape(1,4,2),H).reshape(4,2)

def warp_rgba(image,H,size=(546,483),upscale=3):
    """Premultiplied-alpha warp with downsample; same transform for all skins."""
    w,h=size
    data=np.asarray(image.convert("RGBA"),np.float32)
    data[:,:,:3] *= data[:,:,3:4]/255.0
    scale=np.diag([upscale,upscale,1.0]).astype(np.float64)
    big=cv2.warpPerspective(data,scale@H,(w*upscale,h*upscale),
                           flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,
                           borderValue=(0,0,0,0))
    small=cv2.resize(big,(w,h),interpolation=cv2.INTER_AREA)
    a=small[:,:,3:4]
    rgb=np.where(a>0.005,small[:,:,:3]*255/np.maximum(a,0.005),0)
    return Image.fromarray(np.uint8(np.clip(np.dstack((rgb,a)),0,255)),"RGBA")

def warp_mask(image_mask,H,size=(546,483),upscale=3):
    w,h=size
    mask=np.asarray(image_mask.convert("L"),np.uint8)
    sc=np.diag([upscale,upscale,1.0]).astype(np.float64)
    big=cv2.warpPerspective(mask,sc@H,(w*upscale,h*upscale),
                 flags=cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
    small=cv2.resize(big,(w,h),interpolation=cv2.INTER_AREA)
    # binary mask is canonical for both photo/empty and skin hole.
    return Image.fromarray(np.uint8(small>=128)*255,"L")

def fit_photo(image,size=(110,83)):
    w,h=size;src=image.convert("RGB")
    scale=max(w/src.width,h/src.height)
    rw,rh=math.ceil(src.width*scale),math.ceil(src.height*scale)
    res=src.resize((rw,rh),Image.Resampling.LANCZOS)
    left=(rw-w)//2;top=(rh-h)//2
    return res.crop((left,top,left+w,top+h))

def embed_photo(photo,canvas=(546,483),window_xy=(84,61),window_size=(110,83)):
    fitted=fit_photo(photo,window_size)
    full=Image.new("RGB",canvas,(120,98,75))
    full.paste(fitted,window_xy)
    return full

def projected_photo(photo,H,mask,canvas=(546,483)):
    """An arbitrary registered photo uses H and the canonical derived window mask."""
    rgba=embed_photo(photo,canvas)
    w,h=canvas
    projected=cv2.warpPerspective(np.asarray(rgba),H,(w,h),
                   flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
    alpha=np.asarray(mask.convert("L"))
    out=np.dstack((projected,alpha))
    return Image.fromarray(np.uint8(out),"RGBA")
