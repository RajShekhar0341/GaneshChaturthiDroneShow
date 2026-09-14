"""Natural night-time neighbourhoods, warm windows and unlit asphalt roads.

Keeps the original build_city() four-value return contract. Lit windows are
small mesh faces, so the renderer can occlude them along with the buildings.
The returned point lights are streetlamps rather than transparent windows.
"""
import numpy as np


def build_city():
    rng = np.random.default_rng(14)
    faces, lights, colors, roads = [], [], [], []
    warm = [(218, 173, 112), (180, 153, 113), (242, 205, 148), (145, 135, 115)]

    def box(x, z, w, d, h, base=0, tint=(27, 26, 25)):
        v = np.array([(x,base,z),(x+w,base,z),(x+w,base,z+d),(x,base,z+d),
                      (x,base+h,z),(x+w,base+h,z),(x+w,base+h,z+d),(x,base+h,z+d)])
        for ids, factor in [([0,1,5,4],.80),([1,2,6,5],.66),
                            ([2,3,7,6],.60),([3,0,4,7],.73),([4,5,6,7],1.08)]:
            faces.append((v[ids], tuple(int(c*factor) for c in tint)))

    # Roads separate coherent blocks. Slightly different block sizes avoid a
    # perfectly repeated futuristic grid while remaining deterministic.
    xs = [-330,-251,-174,-93,-12,73,156,245,330]
    zs = [-310,-231,-150,-70,12,96,184,270]
    for x in xs:
        roads.append(np.array([(x,.12,zs[0]),(x,.12,zs[-1])]))
    for z in zs:
        roads.append(np.array([(xs[0],.12,z),(xs[-1],.12,z)]))
    for ix in range(len(xs)-1):
        for iz in range(len(zs)-1):
            bx,bz=xs[ix],zs[iz]
            for dx in [13,39]:
                for dz in [13,40]:
                    x,z=bx+dx+rng.uniform(-2,2),bz+dz+rng.uniform(-2,2)
                    if abs(x)<60 and 0<z<100:
                        continue  # festival courtyard
                    w,d=rng.uniform(15,22),rng.uniform(15,23)
                    floors=int(rng.choice([2,3,4,5,7,10],p=[.28,.27,.23,.13,.06,.03]))
                    h=floors*3.2
                    tint=rng.choice(np.array([(33,30,26),(28,29,29),(38,34,29),(30,27,25)]))
                    box(x,z,w,d,h,tint=tint)
                    # Flat roof, modest parapets and occasional rooftop utility room.
                    box(x,z,w,.45,.7,h,tint)
                    box(x,z+d-.45,w,.45,.7,h,tint)
                    if rng.random()<.45:
                        box(x+w*.45,z+d*.45,w*.28,d*.3,2.2,h,(27,27,26))
                    occupancy=rng.uniform(.27,.68)
                    for y in np.arange(1.2,h-1,3.2):
                        for xx in np.arange(x+2,x+w-1.5,3.7):
                            for zz in [z-.03,z+d+.03]:
                                c=warm[int(rng.integers(len(warm)))] if rng.random()<occupancy else (12,13,14)
                                faces.append((np.array([(xx,y,zz),(xx+1.1,y,zz),(xx+1.1,y+1.4,zz),(xx,y+1.4,zz)]),c))
                        for zz in np.arange(z+2,z+d-1.5,4.1):
                            for xx in [x-.03,x+w+.03]:
                                c=warm[int(rng.integers(len(warm)))] if rng.random()<occupancy else (12,13,14)
                                faces.append((np.array([(xx,y,zz),(xx,y,zz+1.1),(xx,y+1.4,zz+1.1),(xx,y+1.4,zz)]),c))
    for road in roads:
        a,b=road
        for f in np.arange(.025,.99,.055):
            p=a+(b-a)*f
            p[0]+=4 if a[0]==b[0] else 0
            p[2]+=4 if a[2]==b[2] else 0
            p[1]=3.5
            lights.append(p)
            colors.append((235,185,110))
    return faces, np.array(lights), np.array(colors), roads
