#!/usr/bin/env python3
"""Rebuild four conceptual technical diagrams with system Python/matplotlib."""
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', '/tmp/rvi-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parent
BLUE, RED, INK = '#1f5fa8', '#c0392b', '#333333'
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'DejaVu Sans'],
                     'font.size': 10, 'text.color': INK, 'axes.edgecolor': INK,
                     'lines.linewidth': 1.0, 'savefig.facecolor': 'white'})

def canvas(h=3.4):
    fig, ax = plt.subplots(figsize=(7, h), layout='constrained')
    ax.set(xlim=(0, 14), ylim=(0, 7)); ax.axis('off')
    return fig, ax

def box(ax, x, y, w, h, label, color=INK, size=10):
    ax.add_patch(Rectangle((x,y),w,h,fill=False,edgecolor=color,linewidth=1))
    ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=size)

def arrow(ax, a, b, color=INK):
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':color,'lw':1})

def save(fig,name):
    fig.savefig(ROOT/name,dpi=200,metadata={'Software':'matplotlib'})
    plt.close(fig)

def architecture():
    f,a=canvas(4)
    box(a,.15,.25,5.5,6.4,'',BLUE); box(a,8.05,.25,5.8,6.4,'',BLUE)
    a.text(2.9,6.2,'Raspberry Pi 5 · Ubuntu',ha='center')
    a.text(10.95,6.2,'STM32F446RE · FreeRTOS',ha='center')
    box(a,.65,4,4.5,1.5,'Linux workload\nONNX Runtime\nMobileNetV2')
    box(a,1.55,1.8,2.7,.9,'bridge'); arrow(a,(2.9,4),(2.9,2.7))
    a.plot([7,7],[.15,6.7],ls='--',color=INK,lw=1)
    a.text(7,6.9,'Ranh giới quyền điều khiển',ha='center',fontsize=9)
    arrow(a,(4.25,2.25),(8.55,2.25),BLUE)
    a.text(6.45,3.2,'UART',ha='center',color=BLUE)
    a.text(2.9,.9,'HEARTBEAT\nINFERENCE',ha='center',fontsize=8,color=BLUE)
    box(a,8.55,1.8,1.7,.9,'UART ISR',size=9)
    box(a,11,1.65,2.3,1.2,'bounded\nbuffer',size=9)
    arrow(a,(10.25,2.25),(11,2.25))
    box(a,11,3.4,2.3,.85,'RX task');arrow(a,(12.15,2.85),(12.15,3.4))
    box(a,8.55,4.7,4.75,.8,'supervisor',RED)
    a.annotate('',xy=(10.9,4.7),xytext=(12.15,4.25),arrowprops={'arrowstyle':'->','lw':1,'color':INK})
    box(a,8.55,3.4,1.9,.85,'output/LED',RED,size=9)
    arrow(a,(9.5,4.7),(9.5,4.25),RED)
    save(f,'architecture.png')

def frame():
    f,a=canvas(2.6)
    fields=[('SOF0\nA5',1.5),('SOF1\n5A',1.5),('header\nversion · type · seq · len',4.6),('payload\n≤ 64 byte',3.2),('CRC\n2 byte',2.2)]
    x=.5
    for label,w in fields:box(a,x,3,w,2,label,size=9);x+=w
    a.text(2,5.8,'SOF: 2 byte',ha='center')
    a.annotate('',xy=(11.3,2.1),xytext=(3.5,2.1),arrowprops={'arrowstyle':'|-|','color':BLUE,'lw':1})
    a.text(8.5,1.25,'CRC-16/CCITT-FALSE: version → payload',ha='center',color=BLUE)
    save(f,'frame.png')

def queues():
    f,a=canvas(3)
    a.text(.4,6.2,'FIFO: giữ backlog',color=BLUE)
    for x,label in [(1,'Kết quả mới'),(4.2,'Kết quả chờ'),(7.4,'Kết quả cũ')]:box(a,x,4.4,2.7,1,label,size=9)
    arrow(a,(3.7,4.9),(4.2,4.9));arrow(a,(6.9,4.9),(7.4,4.9));arrow(a,(10.1,4.9),(11.2,4.9))
    a.text(12,4.9,'Gửi UART',ha='center',va='center',fontsize=9)
    a.text(.4,3.1,'Latest-value: thay kết quả chưa gửi',color=BLUE)
    box(a,1,1.3,3.5,1,'Kết quả chưa gửi',RED,size=9)
    box(a,6.5,1.3,3.5,1,'Kết quả mới',BLUE,size=9)
    arrow(a,(6.5,1.8),(4.5,1.8),RED);a.text(5.5,2.5,'Thay thế',ha='center',color=RED,fontsize=9)
    arrow(a,(10,1.8),(11.2,1.8));a.text(12,1.8,'Gửi UART',ha='center',va='center',fontsize=9)
    save(f,'queues.png')

def aoi():
    f,ax=plt.subplots(figsize=(7,3.2),layout='constrained')
    ax.spines[['top','right']].set_visible(False)
    ax.plot([0,2,2,4.8,4.8,7,7,9],[1,3,1.2,4,.8,3,1,3],color=BLUE,lw=1.2)
    ax.axhline(3.4,ls='--',color=RED,lw=1)
    ax.text(6,3.55,'Ngưỡng độ tươi',color=RED)
    ax.set(xlim=(0,9.3),ylim=(0,4.5),xlabel='Thời gian',ylabel='Tuổi dữ liệu (AoI)',xticks=[],yticks=[])
    save(f,'aoi.png')

if __name__=='__main__':
    architecture();frame();queues();aoi()
