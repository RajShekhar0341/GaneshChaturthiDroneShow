"""Procedural drone artwork. World axes: X right, Y up, Z depth."""
import numpy as np
import pygame

GOLD = (255, 183, 55)
CYAN = (65, 222, 255)
PINK = (255, 73, 167)


def path(vertices, spacing=1.5):
    out = []
    for a, b in zip(vertices[:-1], vertices[1:]):
        a, b = np.array(a), np.array(b)
        n = max(2, int(np.linalg.norm(b-a)/spacing))
        out.extend(a + (b-a)*t for t in np.linspace(0, 1, n, endpoint=False))
    return np.array(out)


def ellipse(x, y, rx, ry, n=90):
    t = np.linspace(0, 2*np.pi, n)
    return np.column_stack((x+rx*np.cos(t), y+ry*np.sin(t)))


def figure(curves, center, scale=1, depth=0):
    p = np.concatenate(curves) * scale + np.array(center)
    return np.column_stack((p, np.full(len(p), depth)))



def girl():
    """Standing right-facing profile inspired by the supplied child photograph."""
    cs=[
        # Forehead, small nose, lips and chin explicitly point toward Bappa.
        curve([(-10,48),(-2,54),(7,50),(10,43),(15,38),(11,36),(12,32),(8,28),(1,27),(-3,29)]),
        curve([(-3,29),(-4,22),(6,19),(8,26)]),
        curve([(-11,47),(-16,41),(-15,30),(-11,24),(-5,28)]),
        ellipse(6,42,2.7,2,12), ellipse(7,42,.7,1,5),
        curve([(3,46),(7,47),(9,46)]),ellipse(9,48,.7,.7,5),
        ellipse(-4,36,2.8,4,12),ellipse(-4,29,1.5,2.7,10),
        # Shoulder straps and fitted bodice; both hands hold a welcome plate.
        curve([(-4,22),(-11,18),(-11,5),(6,3),(9,17),(6,20)]),
        curve([(-7,20),(-6,12),(5,11),(7,19)]),
        curve([(8,17),(14,8),(24,13),(29,17),(27,19),(22,17),(16,14),(12,22)]),
        curve([(-8,17),(-4,7),(11,8),(24,14)]),
        ellipse(22,14,1.2,2.5,8),
        # Full colourful skirt, upright legs and right-facing feet.
        curve([(-11,5),(-18,-12),(-23,-29),(-10,-33),(5,-34),(20,-30),(13,-12),(6,3)]),
        curve([(-10,-33),(-9,-43),(-2,-43),(1,-42),(-4,-40),(-3,-34)]),
        curve([(7,-34),(8,-42),(15,-42),(18,-40),(12,-39),(13,-32)]),
        curve([(-4,24),(0,19),(5,22)]),
    ]
    # Short curls gathered behind her head, as in the reference.
    for x,y,r in [(-12,49,4),(-7,54,4),(-1,56,3.5),(4,54,3),(-16,44,3.5),(-18,38,3),(-17,32,3.5),(-13,27,3)]:
        cs.append(ellipse(x,y,r,r,12))
    for x in [-10,-3,4,11]:
        cs.append(curve([(x*.5,2),(x,-12),(x*1.35,-28)]))
    for x,y in [(-8,-10),(4,-18),(-13,-25),(11,-25)]:
        cs.append(curve([(x,y+4),(x+3,y),(x,y-4),(x-3,y),(x,y+4)]))
        # Bottom-right, facing left toward Ganpati.
    points = figure(cs, (0, 0), 0.87, 10)
    points[:, 0] = 108 - points[:, 0]
    points[:, 1] += 125
    return points


def lotus():
    curves=[]
    for x in [-40,-20,0,20,40]:
        curves.append(path([(0,-8),(x-14,5),(x,20-abs(x)*.17),(x+14,5),(0,-8)]))
    return figure(curves, (12, 104), 0.9, 10)

def mandala():
    a=np.linspace(0,2*np.pi,260)
    r=95+7*np.cos(12*a)
    p=np.column_stack((19+r*np.cos(a),187+r*np.sin(a),np.full(len(a),22)))
    return p


def text_points(text, y, width, color, x_offset=0):
    font=pygame.font.Font(None,80)
    surf=font.render(text,True,'white')
    pixels=pygame.surfarray.array_alpha(surf)
    x, row=np.where(pixels[::3,::3]>100)
    x=x*3; row=row*3
    scale=width/surf.get_width()
    p=np.column_stack(((x-surf.get_width()/2)*scale+x_offset,y+(surf.get_height()/2-row)*scale,np.full(len(x),32)))
    return p, color


def build():
    return [
        ('halo',mandala(),CYAN,10),
        ('girl',girl(),PINK,18),
        ('ganesha',ganesha(),GOLD,29),
        ('lotus',lotus(),PINK,32),
        ('mouse',mouse(),(165,191,225),37),
        ('brand',*text_points('Perfecto Research',286,198,GOLD,-70),47),
        ('wish',*text_points('Wishing Everyone a Very',268,149,(220,210,255),-70),52),
        ('festival',*text_points('Happy Vinayaka Chavithi',85,160,GOLD,-75),56),
        ('morya',*text_points('Ganpati Bappa Morya!',71,110,PINK,-50),65),
    ]

# V2 artwork: rounded baby-Ganesha proportions inspired by the supplied
# figurine, with the separated light choreography of the drone reference.
def curve(points, spacing=2.0):
    """Catmull–Rom spline resampled at constant arc length for evenly spaced drones."""
    v=np.array(points,dtype=float)
    v=np.vstack((v[0],v,v[-1]))
    result=[]
    for i in range(1,len(v)-2):
        a,b,c,d=v[i-1:i+3]
        for t in np.linspace(0,1,24,endpoint=False):
            result.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
    result=np.vstack((result,points[-1]))
    dist=np.r_[0,np.cumsum(np.linalg.norm(np.diff(result,axis=0),axis=1))]
    at=np.arange(0,dist[-1],spacing)
    return np.column_stack([np.interp(at,dist,result[:,k]) for k in range(2)])


def ganesha():
    """
    Reference-inspired baby Ganpati drone outline.
    Matches the pose and major details, not the photograph's exact
    textures, colours or 3D appearance.
    Requires the existing curve(), ellipse(), figure() and NumPy.
    """
    curves = [
        # Rounded crown and golden top ornament.
        curve([
            (-31, 43), (-30, 60), (-22, 74), (-8, 82),
            (10, 84), (26, 76), (35, 62), (37, 44)
        ]),
        curve([
            (-30, 54), (-17, 60), (0, 63),
            (19, 61), (34, 55)
        ]),
        curve([
            (-28, 59), (-13, 66), (4, 68),
            (21, 65), (32, 60)
        ]),
        curve([
            (-15, 81), (-17, 86), (-12, 91),
            (-7, 98), (0, 94), (7, 89), (5, 84)
        ]),
        ellipse(-5, 82, 14, 3, 30),

        # Central teardrop crown jewel.
        curve([
            (13, 64), (5, 69), (4, 77), (10, 86),
            (14, 90), (20, 84), (24, 76),
            (22, 69), (13, 64)
        ]),
        ellipse(14, 76, 5, 8, 24),

        # Hairline and curved forelock.
        curve([
            (-29, 52), (-31, 43), (-30, 31),
            (-26, 24), (-25, 37), (-18, 49)
        ]),
        curve([
            (5, 59), (11, 51), (21, 48),
            (27, 50), (19, 52), (14, 59)
        ]),

        # Large left ear with a softly folded inner rim.
        curve([
            (-29, 43), (-43, 53), (-59, 50),
            (-68, 43), (-62, 33), (-57, 17),
            (-48, 5), (-38, 7), (-30, 19)
        ]),
        curve([
            (-33, 36), (-44, 44), (-56, 42),
            (-58, 36), (-49, 32), (-46, 20),
            (-39, 14)
        ]),

        # Smaller far ear in three-quarter view.
        curve([
            (35, 43), (44, 47), (52, 40),
            (55, 33), (47, 29), (44, 18),
            (37, 12), (33, 18)
        ]),
        curve([(39, 35), (45, 39), (49, 34), (43, 24)]),

        # Cheeks, forehead and rounded jaw.
        curve([
            (-23, 48), (-13, 54), (2, 57),
            (19, 54), (31, 47), (35, 35)
        ]),
        curve([
            (-26, 31), (-27, 18), (-21, 8),
            (-10, 1), (2, -1), (12, 3)
        ]),
        curve([(34, 28), (37, 18), (33, 8), (26, 4)]),

        # Expressive eyes looking toward the right.
        ellipse(-9, 28, 7, 9, 30),
        ellipse(-6.5, 27.5, 3.6, 5.5, 20),
        ellipse(-5, 30, 1.2, 1.5, 10),
        ellipse(24, 26, 4.8, 7.5, 26),
        ellipse(25.5, 25.5, 2.6, 4.5, 16),
        ellipse(26, 28, 0.9, 1.2, 8),
        curve([(-18, 29), (-15, 36), (-8, 38), (-2, 34)]),
        curve([(19, 32), (23, 35), (28, 33)]),

        # Eyebrows and forehead tilak.
        curve([(-18, 44), (-11, 47), (-4, 45)]),
        curve([(22, 44), (27, 43), (30, 40)]),
        curve([(7, 46), (7, 41), (10, 40), (12, 45)]),
        curve([(12, 46), (13, 40), (16, 41), (17, 46)]),
        ellipse(12, 37, 1, 1.4, 8),

        # Long trunk curling upward to the right.
        curve([
            (8, 26), (7, 15), (10, 2),
            (17, -7), (28, -12), (40, -11),
            (50, -6), (54, 1), (52, 6),
            (48, 7), (46, 3), (47, 0),
            (40, -3), (31, -3), (25, 2),
            (23, 12), (22, 20)
        ]),
        ellipse(50, 2, 1.6, 2.6, 12),
        curve([(10, 14), (15, 15), (20, 14)]),
        curve([(11, 9), (16, 10), (21, 9)]),
        curve([(13, 4), (18, 5), (22, 4)]),

        # Small tusks and smile.
        curve([
            (-4, 12), (-2, 5), (2, 3),
            (3, 7), (0, 13), (-4, 12)
        ]),
        curve([(29, 12), (32, 6), (35, 5), (33, 11)]),
        curve([(-6, 7), (-2, 0), (5, -3), (10, -1)]),

        # Plump seated torso.
        curve([
            (-19, -3), (-30, -11), (-31, -27),
            (-24, -40), (-9, -46), (9, -46),
            (22, -38), (27, -23), (23, -15)
        ]),
        ellipse(3, -32, 2, 1.7, 12),

        # Left arm holding a bowl of sweets.
        curve([
            (-25, -6), (-38, -8), (-45, -18),
            (-44, -28), (-35, -34), (-23, -33)
        ]),
        curve([
            (-29, -15), (-34, -20), (-33, -26),
            (-25, -29), (-19, -25), (-17, -20)
        ]),
        curve([
            (-29, -27), (-24, -32), (-13, -33),
            (-6, -28), (-4, -22), (-29, -22)
        ]),
        ellipse(-17, -22, 12, 3, 28),
        ellipse(-16, -18, 7, 6, 22),
        ellipse(-16, -12, 2, 1.5, 10),
        curve([(-32, -23), (-27, -25), (-23, -24)]),
        curve([(-32, -26), (-27, -28), (-23, -27)]),

        # Right arm extended toward the companion in the reference.
        curve([
            (24, -16), (33, -21), (43, -19),
            (49, -12), (53, -10), (58, -12)
        ]),
        curve([
            (24, -29), (35, -32), (45, -28),
            (52, -21), (58, -19), (61, -15),
            (58, -12)
        ]),
        curve([(47, -14), (53, -14), (57, -16)]),

        # Rounded dhoti and crossed legs.
        curve([
            (-23, -38), (-39, -39), (-49, -48),
            (-47, -61), (-36, -70), (-21, -70),
            (-10, -61), (0, -55)
        ]),
        curve([
            (8, -44), (23, -40), (37, -43),
            (44, -54), (39, -65), (28, -68),
            (16, -62), (4, -58)
        ]),
        curve([
            (-43, -48), (-36, -44), (-27, -45),
            (-20, -55), (-20, -64)
        ]),
        curve([(14, -49), (25, -46), (35, -49), (38, -55)]),

        # Central sash and fabric folds.
        curve([
            (-5, -43), (-8, -52), (-6, -63),
            (1, -69), (7, -66), (4, -55), (5, -45)
        ]),
        curve([(-2, -47), (-3, -56), (1, -64)]),
        curve([(-35, -51), (-30, -57), (-28, -64)]),
        curve([(19, -51), (26, -54), (30, -59)]),

        # Forward-facing feet.
        ellipse(-13, -65, 8, 12, 32),
        ellipse(30, -62, 10, 10, 32),

        # Sacred thread.
        curve([(20, -13), (11, -26), (-2, -36), (-21, -41)]),
    ]

    # Beaded necklace.
    for angle in np.linspace(np.pi, 2 * np.pi, 13):
        x = -2 + 22 * np.cos(angle)
        y = -3 + 22 * np.sin(angle)
        curves.append(ellipse(x, y, 2, 2.2, 9))

    # Floral crown decorations.
    for cx, cy, radius in [
        (-25, 62, 3), (-15, 68, 3),
        (-3, 71, 3.5), (29, 66, 3)
    ]:
        curves.append(ellipse(cx, cy, radius, radius, 12))
        for angle in np.linspace(0, 2 * np.pi, 5, endpoint=False):
            curves.append(
                ellipse(
                    cx + (radius + 1.4) * np.cos(angle),
                    cy + (radius + 1.4) * np.sin(angle),
                    1.6, 1.8, 7
                )
            )

    # Bangles and upper-arm jewellery.
    curves.extend([
        curve([(-41, -14), (-36, -17), (-32, -18)]),
        curve([(-42, -11), (-37, -14), (-33, -15)]),
        curve([(39, -20), (39, -25), (43, -28)]),
        curve([(42, -18), (42, -23), (46, -26)]),
    ])

    # Toes.
    for x, y, rx, ry in [
        (-18, -60, 2, 2.8), (-14, -57, 2, 2.8),
        (-10, -58, 1.7, 2.5), (-7, -61, 1.5, 2.2),
        (23, -57, 2.4, 2.5), (28, -54, 2.3, 2.5),
        (33, -54, 2, 2.3), (37, -57, 1.7, 2)
    ]:
        curves.append(ellipse(x, y, rx, ry, 9))

    # Small embroidered motifs on the dhoti.
    for cx, cy in [(-36, -54), (-29, -65), (25, -48)]:
        curves.append(ellipse(cx, cy, 2, 2, 8))
        for angle in np.linspace(0, 2 * np.pi, 4, endpoint=False):
            curves.append(
                ellipse(
                    cx + 3 * np.cos(angle),
                    cy + 3 * np.sin(angle),
                    1.2, 1.8, 7
                )
            )

    return figure(curves, (12, 178), 0.82, 10)


def mouse():
    cs=[ellipse(0,0,8,12,28),ellipse(-1,15,8,7,24),
        ellipse(5,22,5,6,18),ellipse(-6,22,4,5,16),
        curve([(-7,16),(-14,13),(-7,10)]),ellipse(-5,16,1,1,6),
        curve([(7,-4),(16,-1),(18,9),(23,11)]),
        curve([(-5,-10),(-9,-13),(1,-13),(3,-10)]),
        curve([(-5,1),(-12,4),(-13,7)])]
    return figure(cs,(58,122),.7,-1)
