"""Kitchen Rush — a mouse-and-keyboard arcade game drawn with Tkinter Canvas."""
import math
import time
import tkinter as tk
from engine import Kitchen, DISHES, LABELS, UPGRADES
import progress

W, H = 1100, 760
CREAM = '#F6F1E6'
INK = '#263E35'
MUTED = '#758078'
ORANGE = '#DC613F'
GREEN = '#36876A'
YELLOW = '#F5C65D'
WHITE = '#FFFCF5'
COLORS = {'burger': '#EFC28C', 'noodles': '#F0D367', 'salad': '#AFCAA0'}

class GameApp:
    def __init__(self, root):
        self.root = root
        root.title('Kitchen Rush · The little kitchen with big energy')
        root.geometry('1100x760'); root.minsize(880, 620)
        root.configure(bg=CREAM)
        self.canvas = tk.Canvas(root, bg=CREAM, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.screen = 'menu'; self.paused = False; self.help = False
        self.game = None; self.records = progress.load()
        self.sound = True; self.notice = ''; self.notice_until = 0
        self.particles = []; self.buttons = []; self.hover = (-1,-1)
        self.scale = 1; self.ox = 0; self.oy = 0; self.clock = 0
        self.last = time.monotonic(); self.last_state = None
        self.canvas.bind('<Motion>', self.motion)
        self.canvas.bind('<Button-1>', self.click)
        root.bind('<KeyPress>', self.key)
        root.bind('<FocusOut>', self.focus_out)
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.loop()

    def close(self):
        if self.game: progress.save(self.game)
        self.root.destroy()

    def focus_out(self, event):
        if self.screen == 'game' and self.game.state == 'playing': self.paused = True

    def motion(self, event):
        self.hover = ((event.x-self.ox)/self.scale, (event.y-self.oy)/self.scale)
        cursor = 'hand2' if any(x<=self.hover[0]<=x+w and y<=self.hover[1]<=y+h for x,y,w,h,fn in self.buttons) else ''
        self.canvas.configure(cursor=cursor)

    def click(self, event):
        self.canvas.focus_set()
        x,y = (event.x-self.ox)/self.scale, (event.y-self.oy)/self.scale
        for bx,by,bw,bh,fn in reversed(self.buttons):
            if bx<=x<=bx+bw and by<=y<=by+bh:
                fn(); break

    def key(self, event):
        key = event.keysym.lower()
        if key == 'm': self.toggle_sound(); return
        if key == 'h': self.toggle_help(); return
        if key == 'escape':
            if self.help: self.help = False
            elif self.screen == 'game' and self.game.state == 'playing': self.paused = not self.paused
            return
        if self.help: return
        if key in ('p', 'space') and self.screen == 'game' and self.game.state == 'playing':
            self.paused = not self.paused; return
        if key == 'return':
            if self.screen == 'menu': self.start()
            elif self.game.state == 'break': self.game.next_shift()
            elif self.game.state == 'over': self.start()
            elif self.paused: self.paused = False
            return
        if self.screen == 'game' and not self.paused and self.game.state == 'playing':
            if key in ('1','a'): self.game.work(0)
            elif key in ('2','s'): self.game.work(1)
            elif key in ('3','d'): self.game.work(2)

    def start(self):
        if self.game: progress.save(self.game)
        self.game = Kitchen(); self.screen = 'game'; self.paused = False; self.help = False
        self.particles.clear(); self.notice = 'Match the tickets. Tap a station to start cooking!'
        self.notice_until = self.clock + 4; self.last_state = 'playing'

    def menu(self):
        if self.game: progress.save(self.game)
        self.records = progress.load(); self.screen = 'menu'; self.paused = False

    def toggle_sound(self): self.sound = not self.sound
    def toggle_help(self): self.help = not self.help

    def rr(self,x,y,w,h,fill,outline='',r=18,width=1):
        r=min(r,w/2,h/2)
        pts=[x+r,y,x+w-r,y,x+w,y,x+w,y+r,x+w,y+h-r,x+w,y+h,x+w-r,y+h,x+r,y+h,x,y+h,x,y+h-r,x,y+r,x,y]
        return self.canvas.create_polygon(pts,smooth=True,fill=fill,outline=outline,width=width)

    def text(self,x,y,value,size=16,color=INK,weight='normal',anchor='nw',font='Helvetica',width=None):
        options=dict(text=value,fill=color,font=(font,max(8,round(size*self.scale)),weight),anchor=anchor)
        if width: options['width']=width*self.scale
        return self.canvas.create_text(x,y,**options)

    def oval(self,x,y,w,h,color,outline='',width=1):
        return self.canvas.create_oval(x,y,x+w,y+h,fill=color,outline=outline,width=width)

    def line(self,*coords,fill=INK,width=2): self.canvas.create_line(*coords,fill=fill,width=width*self.scale,capstyle='round',smooth=True)

    def button(self,x,y,w,h,label,fn,color=INK,fg=WHITE,enabled=True):
        hovered=x<=self.hover[0]<=x+w and y<=self.hover[1]<=y+h
        self.rr(x,y+(2 if hovered else 4),w,h,'#D7D6C9',r=13)
        self.rr(x,y,w,h,color if enabled else '#DEDCD2',r=13)
        self.text(x+w/2,y+h/2,label,14,fg if enabled else MUTED,'bold','center')
        if enabled: self.buttons.append((x,y,w,h,fn))

    def dish(self,kind,x,y,s=1):
        # Original vector food art; no downloaded assets or image dependencies.
        def o(a,b,w,h,c): self.oval(x+a*s,y+b*s,w*s,h*s,c)
        def r(a,b,w,h,c,rad=8): self.rr(x+a*s,y+b*s,w*s,h*s,c,r=rad*s)
        if kind == 'burger':
            o(0,65,140,31,'#E1D8C6'); o(4,61,132,28,WHITE)
            r(16,64,108,21,'#BD723C'); r(16,57,108,17,'#EBA54F')
            r(13,47,114,18,'#684231'); r(11,39,118,13,'#7FA258')
            r(17,33,105,10,'#CE6041'); o(17,0,106,73,'#EEB75D'); r(17,32,106,10,'#EEB75D')
            for a,b in [(40,16),(65,10),(87,17),(52,29),(99,29)]: o(a,b,8,3,'#FFF0C7')
        elif kind == 'noodles':
            o(0,59,140,28,'#E1D8C6'); o(11,15,118,77,ORANGE); r(17,15,106,25,ORANGE)
            o(11,5,118,40,'#FEF1D1'); o(20,10,100,29,'#E3B647')
            for i in range(5):
                self.line(x+(30+i*15)*s,y+17*s,x+(45+i*12)*s,y+23*s,x+(29+i*15)*s,y+30*s,fill='#FFE5A0',width=2*s)
            for a,b in [(41,18),(72,28),(98,15)]: o(a,b,9,5,GREEN)
            self.line(x+104*s,y+27*s,x+133*s,y-20*s,fill='#6F5740',width=4*s)
            self.line(x+114*s,y+28*s,x+143*s,y-16*s,fill='#6F5740',width=4*s)
        else:
            o(0,60,140,26,'#E1D8C6'); o(9,14,122,76,'#83A99B'); o(9,7,122,45,'#DBE6C4')
            for a,b in [(19,17),(44,4),(72,17),(94,7),(50,24)]: o(a,b,30,24,'#6B9C55')
            for a,b in [(37,20),(93,24),(69,5)]: o(a,b,16,15,'#D86646'); o(a+4,b+4,4,4,'#F3B36E')
            for a,b in [(23,31),(78,31),(64,19)]: r(a,b,12,10,'#FFF5D5',2)

    def avatar(self,x,y,index):
        shirts=['#E5A38E','#92BCAF','#D5B2CF','#A7B5D8','#C6BE83']
        self.oval(x,y,38,38,shirts[index%5]); self.oval(x+10,y+7,18,21,'#E6B68F')
        self.oval(x+9,y+4,20,12,'#594A3A')
        self.oval(x+14,y+16,2,2,INK); self.oval(x+22,y+16,2,2,INK)
        self.line(x+16,y+24,x+19,y+25,x+22,y+24,fill='#A06F51',width=1)

    def background(self):
        self.canvas.create_rectangle(0,0,W,H,fill=CREAM,outline='')
        for x in range(0,W,45): self.line(x,0,x,H,fill='#EFEADD',width=1)
        for y in range(0,H,45): self.line(0,y,W,y,fill='#EFEADD',width=1)
        self.rr(24,22,1052,66,WHITE,r=20)
        self.text(45,42,'KITCHEN / RUSH',21,INK,'bold')
        self.text(291,48,'A LITTLE KITCHEN. BIG ENERGY.',10,MUTED,'bold')
        self.button(810,36,114,36,'SOUND '+('ON' if self.sound else 'OFF'),self.toggle_sound,color='#ECEEDF',fg=INK)
        self.button(939,36,115,36,'HOW TO PLAY',self.toggle_help,color='#ECEEDF',fg=INK)

    def draw_menu(self):
        self.rr(28,114,1044,531,INK,r=28)
        self.text(68,155,'WELCOME TO YOUR NEXT OBSESSION',11,YELLOW,'bold')
        self.text(65,197,'Small kitchen.',55,WHITE,'bold',font='Georgia')
        self.text(65,267,'Big rush.',70,'#F3C563','bold',font='Georgia')
        self.text(70,370,'Three stations. Hungry guests. One brilliant chef.',17,'#D9E0D3')
        self.text(70,405,'Cook, serve, find your rhythm.\nBuild a streak and turn tips into upgrades.',17,'#D9E0D3')
        self.button(70,490,258,62,'OPEN THE KITCHEN  →',self.start,color=ORANGE)
        self.text(72,577,'ENTER to start   ·   Mouse or 1 / 2 / 3 to play',12,'#C2CFC1')
        self.oval(679,180,318,318,'#3A5747')
        self.oval(703,203,270,270,'#F3C563')
        self.dish('burger',725,291,1.6)
        self.rr(718,472,249,81,WHITE,r=15)
        self.text(741,487,'ORDER UP!',11,ORANGE,'bold')
        self.text(741,512,'Good food. Great timing.',15,INK,'bold')
        for x,y in [(690,191),(981,408),(1010,238)]:
            self.line(x-7,y,x+7,y,fill=YELLOW); self.line(x,y-7,x,y+7,fill=YELLOW)
        self.text(44,680,'PERSONAL BEST',11,MUTED,'bold')
        self.text(44,703,f'{self.records["score"]:,} points',21,INK,'bold')
        self.text(380,680,'FURTHEST SHIFT',11,MUTED,'bold')
        self.text(380,703,str(self.records['shift']),21,INK,'bold')
        self.text(664,680,'THE CHALLENGE',11,MUTED,'bold')
        self.text(664,705,'Keep your five reputation stars shining.',15,INK)

    def draw_game(self):
        g=self.game
        self.text(36,110,f'SHIFT {g.shift:02}',12,ORANGE,'bold')
        self.text(36,131,'Dinner is calling.',25,INK,'bold',font='Georgia')
        self.rr(388,106,167,58,WHITE,r=14)
        self.text(405,116,'SHIFT ENDS IN',9,MUTED,'bold'); self.text(531,134,f'{math.ceil(g.remaining)}s',25,INK,'bold','center')
        self.text(587,111,'REPUTATION',9,MUTED,'bold')
        self.text(582,129,'★'*g.reputation+'☆'*(5-g.reputation),24,ORANGE)
        self.text(766,110,'COINS',9,MUTED,'bold'); self.text(766,132,str(g.wallet),23,INK,'bold')
        self.text(861,110,'SCORE',9,MUTED,'bold'); self.text(861,132,f'{g.score:,}',23,INK,'bold')
        self.button(977,111,85,42,'PAUSE',lambda:setattr(self,'paused',True),color=INK)
        for i in range(5):
            x=34+i*209
            if i>=len(g.orders):
                self.rr(x,188,196,197,'#EBE8DC',r=17)
                self.text(x+98,274,'NEXT GUEST',10,'#A3A797','bold','center')
                continue
            order=g.orders[i]
            self.rr(x+2,193,196,197,'#D8D7C8',r=17); self.rr(x,188,196,197,WHITE,r=17)
            self.avatar(x+13,201,order.id)
            self.text(x+60,204,order.customer,15,INK,'bold')
            self.text(x+60,225,f'TICKET #{order.id:02}',9,MUTED)
            self.dish(order.dish,x+55,256,.6)
            self.text(x+98,319,LABELS[order.dish],13,INK,'bold','center')
            fraction=max(0,order.remaining/order.patience)
            self.rr(x+16,346,164,7,'#ECEBDD',r=3)
            self.rr(x+16,346,max(1,164*fraction),7,GREEN if fraction>.4 else ORANGE,r=3)
            self.text(x+16,363,'WAITING' if fraction>.4 else 'GETTING HUNGRY',8,MUTED,'bold')
            self.text(x+180,363,f'{math.ceil(order.remaining)}s',9,INK,'bold','ne')
        self.text(35,409,'YOUR COOKING STATIONS',11,MUTED,'bold')
        self.text(1060,409,f'STREAK ×{g.combo}  ·  BEST {g.best_combo}',12,ORANGE,'bold','ne')
        for i,s in enumerate(g.stations):
            x=34+i*349; ready=s.phase=='ready'; burned=s.phase=='burned'
            bg='#E0EAD9' if ready else '#ECD5CA' if burned else WHITE
            self.rr(x+2,442,335,211,'#D8D7C8',r=22); self.rr(x,436,335,211,bg,r=22)
            self.rr(x+14,450,30,30,INK,r=8); self.text(x+29,465,str(i+1),14,WHITE,'bold','center')
            self.text(x+57,455,LABELS[s.dish],16,INK,'bold')
            self.dish(s.dish,x+27,505,.75)
            if s.phase=='cooking':
                for n in range(3):
                    dy=(self.clock*20+n*10)%30
                    self.line(x+69+n*12,509-dy,x+65+n*12,500-dy,x+70+n*12,493-dy,fill='#B4BCAF',width=2)
                text='COOKING'; sub=f'{max(0,s.duration-s.elapsed):.1f}s to go'
                frac=s.elapsed/s.duration; color=YELLOW
            elif ready:
                text='SERVE NOW!'; sub='Perfect timing!' if s.elapsed<=1.7 else 'Before it overcooks…'
                frac=1-s.elapsed/g.ready_window; color=GREEN
            elif burned:
                text='OVERDONE'; sub='Tap to clear station'; frac=1; color=ORANGE
            else:
                text='READY TO PREP'; sub='Tap or press '+str(i+1); frac=0; color=GREEN
            self.text(x+156,509,text,12,ORANGE if burned else GREEN if ready else INK,'bold')
            self.text(x+156,534,sub,11,MUTED)
            self.rr(x+156,560,157,8,'#E9E5D9',r=4)
            if frac>0: self.rr(x+156,560,max(1,157*min(1,frac)),8,color,r=4)
            self.text(x+167,613,'CLICK TO SERVE' if ready else 'CLICK TO COOK' if s.phase=='idle' else 'CLICK TO CLEAR' if burned else 'A LITTLE PATIENCE…',10,INK,'bold','center')
            self.buttons.append((x,436,335,211,lambda n=i:g.work(n)))
        self.rr(34,673,1030,58,INK,r=17)
        message=self.notice if self.clock<self.notice_until else 'Serve the matching dish while it’s green. A fresh serve earns extra tips!'
        self.text(53,702,message,13,WHITE,anchor='w')
        self.text(1046,702,'P / SPACE  Pause',10,'#C8D4C6',anchor='e')
        for x,y,age,color in self.particles:
            self.oval(x,y-age*40,5,5,color)

    def draw_break(self):
        g=self.game
        self.rr(32,106,1036,623,INK,r=25)
        self.text(63,138,f'SHIFT {g.shift} / COMPLETE',11,YELLOW,'bold')
        self.text(63,170,'That was delicious.',43,WHITE,'bold',font='Georgia')
        self.text(63,233,f'{g.shift_served} happy guests  ·  +{g.shift_cash} coins earned  ·  {g.shift_missed} missed',16,'#D6DFCF')
        self.text(63,278,'MAKE THE NEXT SHIFT YOUR BEST SHIFT',10,YELLOW,'bold')
        for i,(key,(title,description,base)) in enumerate(UPGRADES.items()):
            x=62+i*330; level=g.levels[key]; maxed=level>=3
            self.rr(x,309,315,245,WHITE,r=18)
            self.text(x+22,331,f'0{i+1} / KITCHEN UPGRADE',10,ORANGE,'bold')
            self.text(x+22,369,title,25,INK,'bold',font='Georgia')
            self.text(x+22,414,description,12,MUTED)
            self.text(x+22,444,'●'*level+'○'*(3-level)+'   Level '+str(level)+'/3',13,GREEN,'bold')
            self.button(x+22,480,271,48,'MAX LEVEL' if maxed else f'UPGRADE · {g.cost(key)} COINS',lambda k=key:g.buy(k),color=ORANGE,enabled=not maxed and g.wallet>=g.cost(key))
        self.text(63,584,f'YOUR WALLET: {g.wallet} COINS',14,YELLOW,'bold')
        self.text(63,614,'Next shift: faster arrivals. One reputation star restored.',13,'#D6DFCF')
        self.button(748,593,284,62,'NEXT SHIFT  →',g.next_shift,color=ORANGE)
        self.button(62,658,168,40,'SAVE & MAIN MENU',self.menu,color='#425C4B')
        self.text(1040,699,'ENTER to continue',10,'#CAD6C6',anchor='e')

    def draw_over(self):
        g=self.game
        self.rr(110,131,880,547,INK,r=30)
        self.text(550,177,'THE LAST ORDER IS OUT',11,YELLOW,'bold','center')
        self.text(550,233,'Every chef has a next shift.',38,WHITE,'bold','center',font='Georgia')
        self.text(550,300,'The guests got hungry. Try serving the shortest patience bar first.',15,'#D6DFCF','normal','center')
        self.text(550,359,f'{g.score:,}',67,YELLOW,'bold','center')
        self.text(550,417,'POINTS EARNED',10,'#D6DFCF','bold','center')
        self.text(550,462,f'Shift {g.shift}   /   {g.served} dishes served   /   Best streak {g.best_combo}',17,WHITE,'normal','center')
        self.button(252,518,285,62,'TRY AGAIN  ↻',self.start,color=ORANGE)
        self.button(559,518,285,62,'MAIN MENU',self.menu,color='#48644F')
        self.text(550,623,'Your personal records are saved on this computer.',12,'#D6DFCF','normal','center')

    def draw_overlay(self,help_mode=False):
        self.buttons=[]
        self.canvas.create_rectangle(0,0,W,H,fill=INK,stipple='gray50',outline='')
        self.rr(211,123,678,520,WHITE,r=25)
        self.text(550,169,'THE RECIPE FOR A GOOD SHIFT' if help_mode else 'Take a little breather.',26,INK,'bold','center',font='Georgia')
        lines=[('01','READ THE TICKETS','Each guest wants a burger, noodles, or a garden bowl.'),
               ('02','COOK & SERVE','Click a station or press 1 / 2 / 3. Tap again when green.'),
               ('03','FIND YOUR RHYTHM','Serve quickly for tips. Missed guests cost a star.'),
               ('04','BUILD YOUR KITCHEN','Spend coins between shifts. Reach the highest score!')]
        if help_mode:
            for i,(n,title,body) in enumerate(lines):
                y=218+i*76; self.text(248,y,n,21,ORANGE,'bold'); self.text(293,y,title,12,INK,'bold'); self.text(293,y+25,body,12,MUTED)
            self.button(249,552,602,52,'GOT IT — LET’S COOK',lambda:setattr(self,'help',False),color=ORANGE)
        else:
            self.dish('noodles',480,224,1)
            self.text(550,353,'Your orders and cooking timers are paused.',16,MUTED,anchor='center')
            self.button(284,411,532,57,'BACK TO THE KITCHEN',lambda:setattr(self,'paused',False),color=ORANGE)
            self.button(284,488,532,47,'END RUN & SAVE RECORD',self.menu,color=INK)
            self.text(550,581,'P / SPACE / ESC to resume   ·   M to toggle sound',12,MUTED,anchor='center')

    def loop(self):
        now=time.monotonic(); dt=min(now-self.last,.15); self.last=now; self.clock+=dt
        if self.screen=='game' and self.game:
            if not self.paused and not self.help: self.game.tick(dt)
            for kind,message in self.game.events:
                self.notice=message; self.notice_until=self.clock+3.2
                if kind in ('perfect','serve'):
                    for i in range(12): self.particles.append((400+i*24,440+(i%3)*10,0,YELLOW if i%2 else ORANGE))
                if self.sound and kind in ('ready','perfect','break'):
                    try: self.root.bell()
                    except tk.TclError: pass
            self.game.events.clear()
            if self.game.state in ('break','over') and self.last_state!=self.game.state:
                if not progress.save(self.game): self.notice='Record could not be saved; check folder permissions.'; self.notice_until=self.clock+8
                self.records=progress.load()
            self.last_state=self.game.state
        self.particles=[(x,y,age+dt,color) for x,y,age,color in self.particles if age<1]
        self.canvas.delete('all'); self.buttons=[]
        cw=max(1,self.canvas.winfo_width()); ch=max(1,self.canvas.winfo_height())
        self.scale=min(cw/W,ch/H); self.ox=(cw-W*self.scale)/2; self.oy=(ch-H*self.scale)/2
        self.background()
        if self.screen=='menu': self.draw_menu()
        elif self.game.state=='break': self.draw_break()
        elif self.game.state=='over': self.draw_over()
        else: self.draw_game()
        if self.help: self.draw_overlay(True)
        elif self.paused and self.screen=='game' and self.game.state=='playing': self.draw_overlay()
        self.canvas.scale('all',0,0,self.scale,self.scale)
        self.canvas.move('all',self.ox,self.oy)
        self.root.after(33,self.loop)

if __name__=='__main__':
    root=tk.Tk()
    GameApp(root)
    root.mainloop()
