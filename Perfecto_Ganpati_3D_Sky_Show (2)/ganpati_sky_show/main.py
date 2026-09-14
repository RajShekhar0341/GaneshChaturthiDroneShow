"""Perfecto Research • a procedural 3D festival, rendered with Pygame/NumPy.
Run: python main.py    |    python main.py --quality low
"""
import argparse
import math
import os
from pathlib import Path
import numpy as np
import pygame
from formations import build, ellipse, GOLD
from city import build_city

DURATION=90.0


def smooth(a,b,t):
    u=np.clip((t-a)/(b-a),0,1)
    return u*u*(3-2*u)


def unit(v):
    return v/max(np.linalg.norm(v),1e-9)


class Show:
    def __init__(self,args):
        pygame.display.init(); pygame.font.init()
        self.args=args; self.size=(1280,720) if args.quality=='high' else (960,540)
        self.screen=pygame.display.set_mode(self.size,pygame.RESIZABLE)
        pygame.display.set_caption('Perfecto Research | Ganesh Chaturthi • 3D Sky Festival')
        self.clock=pygame.time.Clock(); self.time=args.start; self.paused=False
        self.mode=0; self.yaw=0.; self.pitch=0.; self.zoom=1.; self.full=False; self.hud=True
        self.font=pygame.font.Font(None,23); self.small=pygame.font.Font(None,18)
        self.faces,self.windows,self.window_colors,self.roads=build_city()
        self.mesh=np.asarray([f[0] for f in self.faces])
        self.mesh_colors=np.asarray([f[1] for f in self.faces])
        self.mesh_centers=self.mesh.mean(axis=1)
        self.groups=build(); self.rng=np.random.default_rng(8)
        self.sources={}
        for name,p,c,start in self.groups:
            n=len(p); a=np.arange(n)*2.39996
            self.sources[name]=np.column_stack((120*np.cos(a),20+np.arange(n)%30,80+80*np.sin(a)))
        az=self.rng.uniform(-np.pi,np.pi,6500)
        elevation=np.arcsin(self.rng.uniform(.04,1,6500))
        self.stars=np.column_stack((np.cos(elevation)*np.sin(az),np.sin(elevation),np.cos(elevation)*np.cos(az)))*5000
        self.star_colors=np.tile(self.rng.uniform(60,200,(6500,1)),(1,3))
        self.star_colors[:,2]*=1.06

        self.fire_dirs=self.rng.normal(size=(110,3)); self.fire_dirs/=np.linalg.norm(self.fire_dirs,axis=1)[:,None]
        self.resize()

    def resize(self):
        self.w,self.h=self.screen.get_size()
        self.glow=pygame.Surface((max(1,self.w//3),max(1,self.h//3)))
        self.halos={}
        self.background=pygame.Surface((self.w,self.h))
        for y in range(self.h):
            k=y/self.h
            pygame.draw.line(self.background,(int(2+7*k),int(3+7*k),int(8+7*k)),(0,y),(self.w,y))

    def camera(self,t):
        if self.mode==0:
            u=smooth(0,22,t)
            pos=np.array([-145*(1-u)+22*math.sin(t*.065)*u,80+70*u,-260-155*u])
            target=np.array([0,32+113*u,5])
        elif self.mode==1:
            pos=np.array([0,150,-430.]); target=np.array([0,145,10.])
        else:
            a=.28*math.sin(t*.06)+self.yaw
            pos=np.array([math.sin(a)*450,180+self.pitch*150,-math.cos(a)*450])*self.zoom
            target=np.array([0,145,0.])
        if self.mode==0:
            reset=smooth(83,90,t)
            pos=pos*(1-reset)+np.array([-145,80,-260])*reset
            target=target*(1-reset)+np.array([0,32,5])*reset
        self.eye=pos; f=unit(target-pos); right=unit(np.cross(f,[0,1,0]))
        # right is negated to keep world X pointing screen-right.
        right=-right; up=unit(np.cross(f,right))
        self.basis=np.array([right,up,f]); self.focal=min(self.w*.92,self.h*1.1)

    def project(self,p):
        q=(np.asarray(p)-self.eye)@self.basis.T
        z=q[:,2]; den=np.maximum(z,1)
        xy=np.column_stack((self.w/2+self.focal*q[:,0]/den,self.h/2-self.focal*q[:,1]/den))
        return xy,z

    def dots(self,p,color,radius=1,brightness=1,glow=True):
        if brightness<=.01 or not len(p): return
        xy,z=self.project(p)
        mask=(z>3)&(xy[:,0]>2)&(xy[:,0]<self.w-2)&(xy[:,1]>2)&(xy[:,1]<self.h-2)
        pts=xy[mask].astype(int)
        cols=np.asarray(color)
        if cols.ndim==1: cols=np.tile(cols,(len(pts),1))
        else: cols=cols[mask]
        cols=np.clip(cols*brightness,0,255).astype(np.uint8)
        if radius==1:
            # Vectorized pixel write keeps several thousand windows/text drones inexpensive.
            arr=pygame.surfarray.pixels3d(self.screen)
            arr[pts[:,0],pts[:,1]]=cols
            del arr
        else:
            for (x,y),c in zip(pts,cols): pygame.draw.circle(self.screen,c,(int(x),int(y)),radius)
        if glow:
            # Soft Gaussian halos; isolated bright cores retain the drone aesthetic.
            for (x,y),c in zip(pts,cols):
                key=tuple(int(v)//24*24 for v in c)
                if key not in self.halos:
                    sprite=pygame.Surface((11,11))
                    yy,xx=np.mgrid[-5:6,-5:6]
                    fall=np.exp(-(xx*xx+yy*yy)/2.0)*.075
                    pixels=np.clip(fall[:,:,None]*np.array(key),0,255).astype('uint8')
                    pygame.surfarray.blit_array(sprite,pixels)
                    self.halos[key]=sprite
                self.glow.blit(self.halos[key],(int(x//3)-5,int(y//3)-5),special_flags=pygame.BLEND_RGB_ADD)

    def line(self,p,color,width=1,glow=True):
        xy,z=self.project(p)
        if np.any(z<3): return
        pygame.draw.lines(self.screen,color,False,xy.tolist(),width)
        if glow: pygame.draw.lines(self.glow,tuple(int(c*.25) for c in color),False,(xy/3).tolist(),2)

    def city(self,t):
        def polygon(p,c):
            # Clip ground/road polygons against the near plane during flyovers.
            clipped=[]
            for a,b in zip(p,np.roll(p,-1,axis=0)):
                za=float((a-self.eye)@self.basis[2]);zb=float((b-self.eye)@self.basis[2])
                if za>=3: clipped.append(a)
                if (za>=3)!=(zb>=3): clipped.append(a+(b-a)*((3-za)/(zb-za)))
            if len(clipped)>=3:
                xy,_=self.project(np.array(clipped))
                pygame.draw.polygon(self.screen,c,xy)
        polygon(np.array([(-360,0,-340),(360,0,-340),(360,0,290),(-360,0,290)]),(13,15,14))
        # Asphalt ribbons and sparse markings are drawn before buildings.
        for road in self.roads:
            a,b=road; along=unit(b-a); side=np.array([-along[2],0,along[0]])*4
            polygon(np.array([a+side,b+side,b-side,a-side]),(20,20,20))
            for f in np.arange(.01,.98,.065):
                start=a+(b-a)*f
                self.line(np.array([start,start+along*3]),(57,53,43),glow=False)
        # Ground traffic and lamps are occluded by the mesh drawn afterwards.
        for i in range(44):
            a,b=self.roads[i%len(self.roads)]
            f=(t*.012+i*.073)%1
            pos=a+(b-a)*f;pos[1]=.6
            self.dots(np.array([pos]),(235,210,166) if i%2 else (130,45,30),1,glow=False)
        self.dots(self.windows,self.window_colors,1,glow=False)
        # Batch projection avoids repeated NumPy calls for each tiny window.
        xy,z=self.project(self.mesh.reshape(-1,3))
        xy=xy.reshape(-1,4,2);z=z.reshape(-1,4)
        visible=(z.min(axis=1)>3)&(xy[:,:,0].max(axis=1)>0)&(xy[:,:,0].min(axis=1)<self.w)&(xy[:,:,1].max(axis=1)>0)&(xy[:,:,1].min(axis=1)<self.h)
        depth=(self.mesh_centers-self.eye)@self.basis[2]
        order=np.flatnonzero(visible)
        order=order[np.argsort(depth[order])[::-1]]
        for i in order:
            pygame.draw.polygon(self.screen,self.mesh_colors[i],xy[i])
        # Modestly floodlit courtyard, no neon building outlines.
        for k in range(4):
            r=21-k*4;y=4+k*4
            polygon(np.array([(-r,y,40),(r,y,40),(r,y,65),(-r,y,65)]),(78-k*8,64-k*7,43-k*5))

    def performance(self, t):
        end = 1 - smooth(83, 90, t)
        text_groups = {"brand", "wish", "festival", "morya"}

        # --------------------------------------------------
        # Drone formations
        # --------------------------------------------------
        for name, target, color, start in self.groups:
            if t < start:
                continue

            u = smooth(start, start + 8, t)

            p = (
                self.sources[name] * (1 - u)
                + target * u
            ).copy()

            phase = np.arange(len(p)) * 0.13

            p[:, 2] += np.sin(phase + t) * 2 * (1 - u)

            # Keep letters and the standing girl steady.
            if name not in text_groups and name != "girl":
                p[:, 1] += np.sin(phase + t * 0.8) * 0.22 * u

            # Girl: colourful dress, warm face, purple hair lights.
            if name == "girl":
                palette = np.array([
                    (255, 78, 160),
                    (147, 105, 255),
                    (62, 205, 239),
                    (255, 189, 63),
                    (103, 223, 137),
                ])

                # Recover local coordinates for the mirrored girl.
                local_x = (127 - target[:, 0]) / 0.87
                local_y = (target[:, 1] - 151) / 0.87

                bands = (
                    np.floor((local_x + local_y) * 0.28)
                    .astype(int) % len(palette)
                )
                color = palette[bands].copy()

                face = local_y > 27
                hair = (local_y > 27) & (local_x < -7)

                color[face] = (255, 206, 139)
                color[hair] = (180, 155, 231)

            # Slowly rotating mandala.
            if name == "halo":
                theta = (t - 10) * 0.024

                x = p[:, 0] - 37
                y = p[:, 1] - 187

                p[:, 0] = (
                    37
                    + x * np.cos(theta)
                    - y * np.sin(theta)
                )
                p[:, 1] = (
                    187
                    + x * np.sin(theta)
                    + y * np.cos(theta)
                )

            # Ganpati's gold crown and saffron clothing.
            if name == "ganesha":
                colors = np.tile(
                    np.array(color),
                    (len(target), 1)
                )

                colors[target[:, 1] > 229] = (255, 207, 100)
                colors[target[:, 1] < 165] = (255, 122, 43)
                color = colors

            brightness = smooth(start, start + 2, t) * end

            self.dots(
                p,
                color,
                radius=1,
                brightness=brightness,
                glow=name not in text_groups
            )

        # --------------------------------------------------
        # Diya beside the bottom-right girl's hands
        # --------------------------------------------------
        if 23 < t < 90:
            a = t * 1.7

            cx = 83 + 0.8 * math.cos(a)
            cy = 142 + 0.5 * math.sin(a)
            depth = 10

            plate = ellipse(cx, cy, 7, 1.5, 38)

            plate_points = np.column_stack((
                plate,
                np.full(len(plate), depth)
            ))

            diya_brightness = smooth(23, 26, t) * end

            self.dots(
                plate_points,
                GOLD,
                radius=1,
                brightness=diya_brightness
            )

            flame_height = 6 + 0.35 * math.sin(t * 5)

            flame = np.array([
                (cx,     cy,                depth),
                (cx - 1, cy + 4,            depth),
                (cx,     cy + flame_height, depth),
                (cx + 1, cy + 4,            depth),
                (cx,     cy,                depth),
            ])

            flame_color = tuple(
                int(value * diya_brightness)
                for value in (255, 221, 122)
            )

            self.line(flame, flame_color)

        # --------------------------------------------------
        # Laser fans: wider purple beams on the right
        # --------------------------------------------------
        if t > 12:
            laser_brightness = smooth(12, 15, t) * end

            for side in [-1, 1]:
                for j in range(6):

                    # Same fan geometry on both sides, mirrored by `side`,
                    # kept wide enough to clear the girl figure.
                    base_x = side * (175 + j * 2)

                    top_x = side * (
                        182
                        + j * 30
                        + 7 * math.sin(
                            t * 0.45 + j * 0.3
                        )
                    )

                    base_z = 45
                    top_z = 100
                    beam_color = (113, 39, 122) if side == 1 else (36, 116, 146)

                    beam_color = tuple(
                        int(value * laser_brightness)
                        for value in beam_color
                    )

                    beam = np.array([
                        (base_x, 2, base_z),
                        (top_x, 310, top_z),
                    ])

                    self.line(beam, beam_color)

        # --------------------------------------------------
        # Finale fireworks
        # --------------------------------------------------
        if 62 < t < 87:
            firework_colors = [
                (255, 173, 60),
                (90, 225, 255),
                (255, 95, 183),
                (157, 132, 255),
            ]

            for k in range(4):
                age = (t - 62 + k * 1.1) % 4.4

                if age < 0.15:
                    continue

                side = -1 if k % 2 else 1

                center = np.array([
                    side * (138 + 18 * (k // 2)),
                    235 + 20 * (k % 2),
                    25,
                ])

                particles = center + self.fire_dirs * (age * 16)
                particles[:, 1] -= 3.2 * age * age

                self.dots(
                    particles,
                    firework_colors[k],
                    radius=1,
                    brightness=(1 - age / 4.4) * end
                )

        # --------------------------------------------------
        # Opening rising helix
        # --------------------------------------------------
        if t < 20:
            angles = np.linspace(0, 12 * np.pi, 600)
            radius = 35 + 15 * np.sin(angles * 0.3 + t * 0.2)

            helix = np.column_stack((
                radius * np.cos(angles + t * 0.25),
                30 + angles * 4 + min(t, 10) * 3,
                45 + radius * np.sin(angles + t * 0.25),
            ))

            brightness = (
                (1 - smooth(12, 20, t))
                * smooth(0, 3, t)
            )

            self.dots(
                helix,
                (102, 213, 255),
                radius=1,
                brightness=brightness
            )

    def render(self):
        t=self.time%DURATION; self.camera(t)
        self.screen.blit(self.background,(0,0)); self.glow.fill((0,0,0))
        self.dots(self.stars,self.star_colors,1,glow=False)
        self.city(t); self.performance(t)
        bloom=pygame.transform.smoothscale(self.glow,(self.w,self.h))
        self.screen.blit(bloom,(0,0),special_flags=pygame.BLEND_RGB_ADD)
        # Letterbox and editorial HUD.
        pygame.draw.rect(self.screen,(3,7,16),(0,0,self.w,45))
        pygame.draw.rect(self.screen,(3,7,16),(0,self.h-48,self.w,48))
        if self.hud:
            title=self.font.render('PERFECTO RESEARCH  /  SKY FESTIVAL',True,(199,226,238))
            self.screen.blit(title,(22,14))
            stage=next((label for limit,label in [(18,'01  CITY OF LIGHT'),(29,'02  A LITTLE WELCOME'),(47,'03  BAPPA ARRIVES'),(62,'04  WISHES IN THE SKY'),(83,'05  GANPATI BAPPA MORYA'),(90,'06  UNTIL NEXT TIME')] if t<limit),'')
            s=self.small.render(stage,True,(242,188,105)); self.screen.blit(s,(self.w-s.get_width()-22,17))
            hint='SPACE pause   R replay   C camera   arrows / +/- orbit   F fullscreen   H hide   ESC exit'
            self.screen.blit(self.small.render(hint,True,(136,164,184)),(22,self.h-31))
            stamp=self.small.render(f'{t:04.1f} / 90s'+('  PAUSED' if self.paused else ''),True,(221,195,142))
            self.screen.blit(stamp,(self.w-stamp.get_width()-22,self.h-31))
        pygame.draw.rect(self.screen,(48,166,188),(0,self.h-3,int(self.w*t/DURATION),3))
        pygame.display.flip()

    def run(self):
        running=True; count=0
        while running:
            dt=min(self.clock.tick(60)/1000,.08)
            for e in pygame.event.get():
                if e.type==pygame.QUIT: running=False
                elif e.type==pygame.VIDEORESIZE and not self.full:
                    self.screen=pygame.display.set_mode((max(640,e.w),max(400,e.h)),pygame.RESIZABLE); self.resize()
                elif e.type==pygame.KEYDOWN:
                    if e.key==pygame.K_ESCAPE: running=False
                    elif e.key==pygame.K_SPACE: self.paused=not self.paused
                    elif e.key==pygame.K_r: self.time=0
                    elif e.key==pygame.K_c: self.mode=(self.mode+1)%3
                    elif e.key==pygame.K_h: self.hud=not self.hud
                    elif e.key==pygame.K_f:
                        self.full=not self.full
                        self.screen=pygame.display.set_mode((0,0) if self.full else self.size,pygame.FULLSCREEN if self.full else pygame.RESIZABLE); self.resize()
            keys=pygame.key.get_pressed()
            self.yaw+=(keys[pygame.K_RIGHT]-keys[pygame.K_LEFT])*dt*.5
            self.pitch=float(np.clip(self.pitch+(keys[pygame.K_UP]-keys[pygame.K_DOWN])*dt*.4,-.6,.9))
            self.zoom=float(np.clip(self.zoom+(keys[pygame.K_MINUS]-keys[pygame.K_EQUALS])*dt*.3,.7,1.6))
            if not self.paused and not self.args.screenshot: self.time=(self.time+dt)%DURATION
            self.render(); count+=1
            if self.args.screenshot:
                pygame.image.save(self.screen,self.args.screenshot); running=False
            if self.args.frames and count>=self.args.frames: running=False
        pygame.quit()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quality',choices=['low','high'],default='high')
    parser.add_argument('--start',type=float,default=0,help='Start at a timeline second')
    parser.add_argument('--screenshot',help='Render one frame to a PNG path')
    parser.add_argument('--frames',type=int,default=0,help='Exit after N frames; for smoke checks')
    args=parser.parse_args()
    if args.screenshot: os.environ.setdefault('SDL_VIDEODRIVER','dummy')
    Show(args).run()

if __name__=='__main__': main()
