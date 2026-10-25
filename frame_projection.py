# -*- coding: utf-8 -*-
"""Reusable A18 exhibit geometry. No source files, global state, or UI dependencies.
All geometry points in order: TL, TR, BR, BL (with perspective arbitrary).
"""
import math
import cv2
import numpy as np
from PIL import Image
def _quad(points):
 a=np.asarray(points,np.float32)
 if a.shape!=(4,2):raise ValueError("A quad needs four 2D vertices")
 if abs(float(cv2.contourArea(a)))<1:raise ValueError("Degenerate quad")
 return a
def project_frame(source_rgba, source_outer, source_inner, dest_outer, dest_inner, canvas_size=(546,483),upscale=3):
 """Four common projective strips ensure both outer silhouette and inner photo plane match.
 Do not shift source pixels per skin: all skins must call this with the SAME coordinates.
 """
 so,si,do,di=map(_quad,(source_outer,source_inner,dest_outer,dest_inner))
 W,H=canvas_size;w,h=W*upscale,H*upscale
 sr=np.asarray(source_rgba.convert("RGBA"),np.float32)
 sr[:,:,:3]*=sr[:,:,3:4]/255.
 out=np.zeros((h,w,4),np.float32)
 def destination(p):
  for j in range(4):
   if np.array_equal(p,so[j]):return do[j]
   if np.array_equal(p,si[j]):return di[j]
  raise ValueError("Unmapped point")
 strips=((so[0],so[1],si[1],si[0]),(so[1],so[2],si[2],si[1]),
         (so[3],so[2],si[2],si[3]),(so[0],so[3],si[3],si[0]))
 for strip in strips:
  inp=np.float32(strip);target=np.float32([destination(v) for v in strip])*upscale
  transform=cv2.getPerspectiveTransform(inp,target)
  sample=cv2.warpPerspective(sr,transform,(w,h),flags=cv2.INTER_LINEAR,
              borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
  mask=np.zeros((h,w),np.uint8)
  cv2.fillConvexPoly(mask,np.int32(np.rint(target)),255)
  opacity=mask.astype(np.float32)/255.*(1-out[:,:,3]/255.)
  out[:,:,:3]+=sample[:,:,:3]*opacity[:,:,None]
  out[:,:,3]+=sample[:,:,3]*opacity
 small=cv2.resize(out,(W,H),interpolation=cv2.INTER_AREA)
 a=small[:,:,3:4]
 rgb=np.where(a>.005,small[:,:,:3]*255./np.maximum(a,.005),0)
 return Image.fromarray(np.uint8(np.clip(np.dstack([rgb,a]),0,255)),"RGBA")
def fit_photo(source,window_size):
 """Center-crop arbitrary real user photo to a canonical rectangle, before projection."""
 width,height=window_size
 rgb=source.convert("RGB")
 sf=max(width/rgb.width,height/rgb.height)
 nw,nh=math.ceil(rgb.width*sf),math.ceil(rgb.height*sf)
 resized=rgb.resize((nw,nh),Image.Resampling.LANCZOS)
 x=(nw-width)//2;y=(nh-height)//2
 return resized.crop((x,y,x+width,y+height))
def project_photo_to_window(cropped_photo,target_quad,target_mask):
 """Shared transformation for empty mat, preview photo, and future registered user photo.
 RGBA alpha equals the SAME exact display window mask for all sources.
 """
 target=_quad(target_quad)
 window=np.asarray(cropped_photo.convert("RGB"))
 h,w=window.shape[:2]
 if h<2 or w<2:raise ValueError("Window image too small")
 mask=np.asarray(target_mask.convert("L"))
 H,W=mask.shape
 src=np.float32([[0,0],[w-1,0],[w-1,h-1],[0,h-1]])
 transform=cv2.getPerspectiveTransform(src,target)
 projected=cv2.warpPerspective(window,transform,(W,H),flags=cv2.INTER_LINEAR,
                   borderMode=cv2.BORDER_REPLICATE)
 return Image.fromarray(np.dstack([projected,np.uint8(mask>0)*255]),"RGBA")
def reversed_quad(quad,canvas_width):
 return [[float(canvas_width-x),float(y)] for x,y in _quad(quad)]
