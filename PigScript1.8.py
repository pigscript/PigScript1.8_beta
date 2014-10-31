#!python3.4
#	PigScript1.7
from urllib.request import urlopen
from PIL.ImageGrab import grab
from pymouse import PyMouse
from msvcrt import getch
from io import BytesIO
from os import system
from PIL import Image
import random
import math
import time


def keyboardinput(validinput):
	while True:
		try:
			c=getch().decode()
		except:
			continue
		if c in validinput:
			break
	return c

class picture:

	def __init__(self, filename, source, scale):
		self.name = filename
		self.source = source
		self.scale = scale

	def load(self):
		if self.source==1:
			im = Image.open(self.name)
		else:
			fd = urlopen(self.name)
			image_file = BytesIO(fd.read())
			im=Image.open(image_file)
		im = im.convert('RGBA')
		width, height = im.size
		rec = [[-1 for x in range(width)] for y in range(height)]
		print('Loading picture, please wait')
		pixdata = [[im.getpixel((x,y)) for x in range(width)] for y in range(height)]
		colorwidth=64
		xysample=max(1,min(width//200,height//200))
		samplewidth=width//xysample
		sampleheight=height//xysample
		im1 = Image.new('RGBA',(2*samplewidth,2*sampleheight))
		while True:
			seg=256//colorwidth
			tot = seg*seg*seg
			rgb = [[0,0,0,0,i,0] for i in range(tot)]
			totalpix=0
			for y in range(height):
				for x in range(width):
					r,g,b,a = pixdata[y][x]
					if a>128:
						totalpix+=1
						ind = (r//colorwidth)*seg*seg + (g//colorwidth)*seg + b//colorwidth
						rgb[ind][0]+=r
						rgb[ind][1]+=g
						rgb[ind][2]+=b
						rgb[ind][3]+=1
						rec[y][x]=ind
			avecolor=[]
			for i in range(tot):
				if rgb[i][3]==0:
					avecolor.append([-1,-1,-1])
				else:
					avecolor.append([rgb[i][0]//rgb[i][3],rgb[i][1]//rgb[i][3],rgb[i][2]//rgb[i][3]])
			srgb = sorted(rgb, key = lambda foo: -foo[3])
			imglist=[0.95,0.98,0.99,1]
			pos=[['Upper left','Upper right'],['Lower left','Lower right']]
			xblock,yblock=0,0
			maxcolor=1
			for accuracy in imglist:
				pixcount = 0
				for i in range(tot):
					pixcount += srgb[i][3]
					if i>=maxcolor and pixcount>=accuracy*totalpix:
						maxcolor=i+1
						break
				alist=[]
				los = 1 - pixcount/totalpix
				for ind in range(maxcolor-1):
					alist.append(srgb[ind][4])
				r1,g1,b1,n1=0,0,0,0
				for ind in range(maxcolor-1,tot):
					r1+=srgb[ind][0]
					g1+=srgb[ind][1]
					b1+=srgb[ind][2]
					n1+=srgb[ind][3]
				if n1>0:
					r1 = r1//n1
					g1 = g1//n1
					b1 = b1//n1
				pixcount=0
				segcount=0
				print(pos[xblock][yblock],'image: {} different colors, recovery rate = {:.2%}'.format(maxcolor, 1-los))
				for y in range(sampleheight):
					oldc=-1
					for x in range(samplewidth):
						if rec[xysample*y][xysample*x]==-1:
							im1.putpixel((x+xblock*samplewidth,y+yblock*sampleheight),(255,255,255,0))
							newc=rec[xysample*y][xysample*x]
						elif rec[xysample*y][xysample*x] in alist:
							r,g,b = avecolor[rec[xysample*y][xysample*x]]
							im1.putpixel((x+xblock*samplewidth,y+yblock*sampleheight),(r,g,b,255))
							newc=rec[xysample*y][xysample*x]
						else:
							im1.putpixel((x+xblock*samplewidth,y+yblock*sampleheight),(r1,g1,b1,255))
							newc=100
						if newc!=oldc:
							if oldc!=-1:
								segcount+=1
							oldc=newc
					if oldc!=-1:
						segcount+=1
				estm1 = xysample*xysample*segcount//600 + (width*height*self.scale)//200000
				estm2 = 2 + xysample*xysample*segcount//400 + (width*height*self.scale)//150000
				print('Estimated painting time is {}-{} minutes.\n'.format(estm1,estm2))
				xblock+=1
				if xblock==2:
					xblock=0
					yblock+=1
			im1.show()
			while True:
				n=input('Choose accuracy(between 0-1), or input a number > 1 to further improve output quality\n Accuracy = ')
				try:
					n=float(n)
				except:
					continue
				if n>0:
					break
			if n>1:
				colorwidth=colorwidth//2
				continue
			pixcount=0
			for i in range(tot):
				pixcount+=srgb[i][3]
				if pixcount > totalpix*n:
					break
			maxcolor = i+1
			for ind in range(maxcolor-1,tot):
				r1+=srgb[ind][0]
				g1+=srgb[ind][1]
				b1+=srgb[ind][2]
				n1+=srgb[ind][3]
			if n1>0:
				r1 = r1//n1
				g1 = g1//n1
				b1 = b1//n1
			break
		palette=[]
		for i in range(maxcolor-1):
			n = srgb[i][4]
			r,g,b = avecolor[n]
			palette.append((n,r,g,b))
		palette.append((-1,r1,g1,b1))
		return colorwidth,pixdata, palette

	def crop(self, pixdata, start_x, start_y, end_x, end_y):
		pixblock = [[(255,255,255,255) for x in range(end_x-start_x)] for y in range(end_y-start_y)]
		for y in range(start_y,end_y):
			for x in range(start_x,end_x):
				pixblock[y-start_y][x-start_x] = pixdata[y][x]
		return pixblock
		
	def parse(self, colorwidth, pixblock, palette, ind):
		segments=[]
		height=len(pixblock)
		width=len(pixblock[0])
		num,red,green,blue=palette[ind]
		seg=256/colorwidth
		for j in range(height):
			flag = 0
			for i in range(width):
				r,g,b,a = pixblock[j][i]
				if (num<0 or (r//colorwidth)*seg*seg+(g//colorwidth)*seg+(b//colorwidth)==num) and a>128:
					pixblock[j][i] = (0,0,0,0)
					if flag==0:
						flag = 1
						xl = i
				else:
					if flag==1:
						flag=0
						xr = i-1
						segments.append((j,xl,xr))
			if flag==1:
				xr=i
				segments.append((j,xl,xr))
		return segments, pixblock


class paint:	
	
	def __init__(self, mouse):
		self.mouse = mouse
		self.scr_width, self.scr_height = mouse.screen_size()
		self.center_x = 170 + self.scr_width//2
		self.center_y = self.scr_height//2
		self.wheel_x=0
		self.fonts=[]
		self.colormap=[]
		try:
			f=open('scrinfo.txt').read()
			fn=f.split('\n')
			for lines in fn:
				paras=[int(a) for a in lines.split(',')]
				if paras[0]==self.scr_width and paras[1]==self.scr_height:
					self.wheel_x,self.wheel_y,self.radius=paras[2:5]
			f.close()
		except:
			pass
		if self.wheel_x==0:
			self.setscr()
			f=open('scrinfo.txt','w')
			s=','.join([str(self.scr_width),str(self.scr_height),str(self.wheel_x),str(self.wheel_y),str(self.radius)])
			f.write(s)
			f.close()

	def load_fonts(self):
		self.fonts=open('chars.txt').read().split('\n')

	def setmouse(self, x, y):
		print('To move 1 pixel,  a:left, d:right, w:up, s:down')
		print('To move 10 pixels,  j:left, l:right, i:up, k:down')
		while True:
			try:
				c=getch().decode()
			except:
				continue
			if c=='a':
				x-=1
			elif c=='d':
				x+=1
			elif c=='w':
				y-=1
			elif c=='s':
				y+=1
			elif c=='j':
				x-=10
			elif c=='l':
				x+=10
			elif c=='i':
				y-=10
			elif c=='k':
				y+=10
			elif c=='\r' or c=='\n':
				break
			self.mouse.move(x,y)
		return x,y

	def shift(self, dir, t):
		if dir == 'up':
			self.mouse.move(self.center_x, self.center_y - 318)
		elif dir == 'down':
			self.mouse.move(self.center_x, self.center_y + 318)
		elif dir == 'left':
			self.mouse.move(self.center_x - 318, self.center_y)
		elif dir == 'right':
			self.mouse.move(self.center_x + 318, self.center_y)
		time.sleep(t)
		self.mouse.move(self.center_x, self.center_y)

	def setscr(self):
		print('I need more information about your screen size.')
		print('Please move your mouse near the center of the color wheel, then press enter.')
		x,y = self.setmouse(502 + self.scr_width//2,212 + self.scr_height//2)
		self.mouse.click(x,y-15)
		time.sleep(0.1)
		im=grab()
		maxr, maxj, cx, lv = 0, 0, 0, 0
		for j in range(-8,9):
			data=[sum(im.getpixel((x-50+k,y+j))) for k in range(100)]
			left, right = -1,0
			for k in range(100):
				if data[k]<60:
					if left<0:
						left=k
					elif k-left>10:
						right=k
						break
			radius = right-left
			if radius>maxr:
				maxr=radius
				maxj = j
				cx=(left+right+1)//2
			elif radius==maxr:
				lv+=1
		x += cx-50
		y += maxj+lv//2
		self.mouse.click(x+15,y)
		time.sleep(0.1)
		im=grab()
		data=[sum(im.getpixel((x,y+j-40))) for j in range(81)]
		top,bottom=-1,-1
		for k in range(40):
			if data[40-k]<300:
				if top<0:
					top=k
			if data[40+k]<200:
				if bottom<0:
					bottom=k
		y = y+(bottom-top)//2
		self.mouse.click(x,y)
		self.wheel_x = x
		self.wheel_y = y
		self.radius = (top+bottom)//2

	def setcolor(self, r, g, b, rainbow=0):
		wheel_x = self.wheel_x
		wheel_y = self.wheel_y
		wheel_r = self.radius
		bar_x = self.wheel_x+wheel_r+15
		if rainbow == 1:
			xt = wheel_x + int(wheel_r*math.cos(2*math.pi*r))
			yt = wheel_y - int(wheel_r*math.sin(2*math.pi*r))
			self.mouse.click(xt,yt)
			self.mouse.click(bar_x,wheel_y)
			return
		r,g,b = r/255, g/255, b/255
		maxc = max(r, g, b)
		minc = min(r, g, b)
		z = (maxc+minc)/2
		if minc == maxc:
			x,y,xn,yn = 0,0,0,0
		else:
			sc = (maxc-minc)/math.sqrt(r*r+g*g+b*b-r*g-g*b-b*r)
			x = (r - g/2 - b/2) * sc
			y = (math.sqrt(3)/2) * (g-b) * sc
			rd = math.sqrt(x*x+y*y)
			rn = math.sqrt(rd)
			xn = x/rn
			yn = y/rn
		xt = wheel_x + int(wheel_r*xn)
		yt = wheel_y - int(wheel_r*yn)
		zt = wheel_y + wheel_r - round(2*wheel_r*z)
		self.mouse.click(xt,yt)
		self.mouse.click(bar_x,zt)

	def drawline(self, startx, starty, endx, endy):
		self.mouse.press(startx, starty)
		self.mouse.drag(endx, endy)
		time.sleep(0.1)
		self.mouse.release(endx, endy)
		if abs(endx-startx) > 40 or abs(endy-starty)>40:
			self.mouse.click(endx,endy)
			time.sleep(0.1)

	def paraplot(self,fx,fy,start=0,end=2*math.pi,cx=0,cy=0,speed=1):
		if cx==0:
			cx=self.center_x
			cy=self.center_y
		t=start
		self.mouse.press(cx+round(fx(t)), cy+round(fy(t)))
		time.sleep(0.1)
		while t<=end:
			self.mouse.drag(cx+round(fx(t)), cy+round(fy(t)))
			if (end-start)<1 and (end-start)>0.4:
				dt=speed*(end-start)/50
			else:
				dt=speed*0.01
			i=2
			for i in range(2,10):
				dst = 0
				for j in range(1,i):
					r = 300/(math.sqrt(fx(t)*fx(t)+fy(t)*fy(t))+200)
					x1 = fx(t)
					y1 = fy(t)
					x2 = fx(t+i*dt)
					y2 = fy(t+i*dt)
					x3 = fx(t+j*dt)
					y3 = fy(t+j*dt)
					if x1==x2 and y1==y2:
						dst=0
					else:
						dst = abs(x3*(y1-y2)-y3*(x1-x2)+x1*y2-x2*y1)/math.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2))
					if dst > 0.05/r:
						break
				if dst>0.05/r:
					break
			t+= (i-1)*dt
			time.sleep(0.02)
		self.mouse.drag(cx+round(fx(end)),cy+round(fy(end)))
		time.sleep(0.1)
		self.mouse.release(cx+round(fx(end)),cy+round(fy(end)))

	def polar(self,f,start=0,loop=1,speed=1,cx=0,cy=0,dir=1):
		theta=start
		if loop<0:
			end=-2*math.pi*loop
		else:
			end=start+loop*2*math.pi
		if cx==0:
			cx=self.center_x
			cy=self.center_y
		self.mouse.press(round(cx + f(start)*math.cos(start)), round(cy-dir*f(start)*math.sin(start)))
		mindst = 2
		while theta<=end:
			x = round(cx + f(theta)*math.cos(theta))
			y = round(cy - dir*f(theta)*math.sin(theta))
			self.mouse.drag(x,y)
			dtheta=0.009*speed
			i=2
			for i in range(2,10):
				dst = 0
				for j in range(1,i):
					x1 = f(theta)*math.cos(theta)
					y1 = f(theta)*math.sin(theta)
					x2 = f(theta+i*dtheta)*math.cos(theta+i*dtheta)
					y2 = f(theta+i*dtheta)*math.sin(theta+i*dtheta)
					x3 = f(theta+j*dtheta)*math.cos(theta+j*dtheta)
					y3 = f(theta+j*dtheta)*math.sin(theta+j*dtheta)
					if x1==x2 and y1==y2:
						dst=1
					else:
						dst = abs(x3*(y1-y2)-y3*(x1-x2)+x1*y2-x2*y1)/math.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2))
					if dst > 0.05:
						break
				if dst>0.05:
					break
			theta += (i-1)*dtheta
			time.sleep(0.01)
		x=cx+round(f(end)*math.cos(end))
		y=cy-dir*round(f(end)*math.sin(end))
		self.mouse.drag(x,y)
		time.sleep(0.1)
		self.mouse.release(x,y)

	def typeletter(self,ch,llx,lly,scx,scy,speed=7):
		if self.fonts==[]:
			self.load_fonts()
		letter=self.fonts[ord(ch)-32].split(',')
		vertex=int(letter[0])-1
		width=int(letter[1])
		m=self.mouse
		ind=2
		press=0
		while ind<111:
			a=int(letter[ind])
			if a==-1:
				if press==1:
					m.release(nx,ny)
					time.sleep(0.02)
					press=0
			else:
				vertex-=1
				b=int(letter[ind+1])+7
				nx,ny=llx+round(scx*a/width),lly-round(scy*b/32)
				if press==0:
					m.press(nx,ny)
					press=1
					prex,prey=nx,ny
				else:
					m.drag(nx,ny)
					d=max(nx-prex,ny-prey)
					prex,prey=nx,ny
					if d>10:
						time.sleep(0.01*speed)
					elif d>5:
						time.sleep(0.008*speed)
					else:
						time.sleep(0.005*speed)
			ind+=2
		if press==1:
			m.release(nx,ny)

	def drawblock(self, segments, startx, starty, red, green, blue, scale=2):
		if len(segments)>0:
			self.setcolor(red,green,blue)
		for seg in segments:
			y,xl,xr = seg
			self.drawline(startx+scale*xl, starty+scale*y, startx+scale*xr, starty+scale*y)

	def probe(self, dir, sz=2):
		cx,cy=self.center_x,self.center_y
		if dir=='right':
			dx,dy=1,0
		elif dir=='left':
			dx,dy=-1,0
		elif dir=='down':
			dx,dy=0,1
		else:
			dx,dy=0,-1
		self.mouse.move(1,100)
		time.sleep(0.3)
		im=grab()
		if dir=='right' or dir=='left':
			background=[im.getpixel((cx+(k-250)*dx,cy-120)) for k in range(500)]
		else:
			background=[im.getpixel((cx-120,cy+(k-250)*dy)) for k in range(500)]
		rc,gc,bc=im.getpixel((cx+225*dx,cy+225*dy))
		n=2
		while True:
			w=256//n
			colrec=[0]*n*n*n
			for r,g,b in background:
				ind=(r//w)*n*n + (g//w)*n + b//w
				colrec[ind]=1
			for k in range(n*n*n):
				if colrec[k]==0:
					break
			if colrec[k]==0:
				break
			n*=2
		r1=(k//(n*n))*w+w//2
		g1=((k//n)%n)*w+w//2
		b1=(k%n)*w+w//2
		r0,g0,b0=background[455]
		self.setcolor(r1,g1,b1)
		wd=max(3-sz,0)
		for i in range(-wd,wd+1):
			if dir=='left' or dir=='right':
				self.drawline(cx+205*dx+i,cy-120-wd,cx+205*dx+i,cy-120+wd)
			else:
				self.drawline(cx-120-wd,cy+205*dy+i,cx-120+wd,cy+205*dy+i)
		for i in range(9):
			self.setcolor(255*((i%4)//2),255*((i%4)//2),255*((i%4)//2))
			if dir=='left' or dir=='right':
				self.drawline(cx+(225+i)*dx,cy-5,cx+(225+i)*dx,cy+5)
			else:
				self.drawline(cx-5,cy+(225+i)*dy,cx+5,cy+(225+i)*dy)
		time.sleep(0.5)
		self.shift(dir,1)
		time.sleep(1)
		while True:
			time.sleep(2)
			self.mouse.move(1,100)
			time.sleep(0.5)
			im = grab()
			if dir=='right' or dir=='left':
				bg2=[im.getpixel((cx+(k-250)*dx,cy-120)) for k in range(500)]
			else:
				bg2=[im.getpixel((cx-120,cy+(k-250)*dy)) for k in range(500)]
			pl,pr=-1,0
			for k in range(500):
				r,g,b=bg2[k]
				if max(abs(r-r1),abs(g-g1),abs(b-b1)) <= w//3:
					if pl==-1:
						pl=k
					pr=k
				else:
					if pl!=-1:
						break
			if dir=='right' or dir=='down':
				k=(pl+pr)//2+1
			else:
				k=(pl+pr)//2-1+(pl+pr)%2
			if pl==-1 or pr>465:
				print('Lost target')
				print(bg2)
				print(r1,g1,b1,w)
				a,b=self.setmouse(cx,cy)
				self.mouse.click(a,b)
				k=160
			if k>350:
				self.shift(dir,0.7)
			elif k>250:
				self.shift(dir,0.6)
			elif k>150:
				self.shift(dir,0.5)
			else:
				break
		self.setcolor(r0,g0,b0)
		for i in range(-wd,wd+1):
			if dir=='left' or dir=='right':
				self.drawline(cx+(k-250)*dx+i,cy-120-wd,cx+(k-250)*dx+i,cy-120+wd)
			else:
				self.drawline(cx-120-wd,cy+(k-250)*dy+i,cx-120+wd,cy+(k-250)*dy+i)
		self.setcolor(rc,gc,bc)
		for i in range(11):
			if dir=='left' or dir=='right':
				self.drawline(cx+(k-231+i)*dx,cy-6,cx+(k-231+i)*dx,cy+6)
			else:
				self.drawline(cx-6,cy+(k-231+i)*dy,cx+6,cy+(k-231+i)*dy)
		return k-55

	def autodraw(self, filename, source, scale=2):
		pic = picture(filename, source, scale)
		colorwidth,pixdata,palette = pic.load()
		height = len(pixdata)
		width = len(pixdata[0])
		cnum = len(palette)
		ulx, uly = 0, 0
		print('Use asdw to move you mouse to the start point, then press enter to start')
		xr, yr = self.setmouse(self.center_x-200,self.center_y-200)
		self.setcolor(0,0,0)
		self.drawline(xr,yr,xr+15,yr)
		self.drawline(xr,yr,xr,yr+15)
		xr = xr-self.center_x+200
		yr = yr-self.center_y+200
		flag=-1
		pixcount=0
		while True:
			flag*=-1
			pixcount=0
			ulx=0
			while True:
				pixcount+=(400-xr)
				sx = max(ulx-1,0)
				sy = max(uly-1,0)
				ex = min(1+ulx+(400-xr)//scale, width-1)
				ey = min(1+uly+(400-yr)//scale, height-1)
				if flag==1:
					pixblock = pic.crop(pixdata,sx,sy,ex,ey)
				else:
					pixblock = pic.crop(pixdata,width-ex-1,sy,width-sx-1,ey)
				for ind in range(cnum):
					seg,pixblock = pic.parse(colorwidth,pixblock,palette,ind)
					red,green,blue = palette[ind][1:]
					if flag==1:
						self.drawblock(seg, self.center_x+xr-200, self.center_y+yr-200, red, green, blue, scale)
					else:
						extra=max(pixcount-width*2,0)
						self.drawblock(seg, self.center_x-200+extra, self.center_y+yr-200, red, green, blue, scale)
				time.sleep(0.5)
				ulx = ulx+(400-xr)//scale
				if ulx>=width:
					break
				if flag==1:
					xr = self.probe('right',sz=scale)
				else:
					xr = self.probe('left',sz=scale)
			uly = uly + (400-yr)//scale
			if uly>=height:
				break
			yr = self.probe('down',sz=scale)
			xr=pixcount-width*scale

	def autowrite(self, text, fontsize=12):
		rowtot=len(text)
		coltot=max([len(line) for line in text])
		height=rowtot*fontsize*3
		width=coltot*fontsize*2
		doc=[[' ' for i in range(coltot+30)] for j in range(rowtot+20)]
		for j in range(rowtot):
			doc[j][:len(text[j])]=text[j][:]
		c=input('What is your pen size?')
		psz=int(c)
		print('Use asdw to move you mouse to the start point, then press enter to start')
		xr, yr = self.setmouse(self.center_x-200,self.center_y-200)
		xr = xr-self.center_x+200
		yr = yr-self.center_y+200
		flag=-1
		rowcount=0
		colcount=0
		ulx,uly=0,0
		rowextra=0
		while True:
			flag*=-1
			ulx=0
			segh=400-yr+rowextra
			rownum=segh//(3*fontsize)
			colextra=0
			colcount=0
			colnum=0
			while True:
				segw=400-xr+colextra
				colnum=segw//(2*fontsize)
				if colnum+colcount>=coltot:
					colnum=coltot-colcount
				if flag==1:
					textblock=[a[colcount:colcount+colnum] for a in doc[rowcount:rowcount+rownum]]
				else:
					textblock=[a[coltot-colcount-colnum:coltot-colcount] for a in doc[rowcount:rowcount+rownum]]
				self.setcolor(0,0,0)
				for j in range(rownum):
					for i in range(colnum):
						if flag==1:
							llx=self.center_x+xr-colextra-200+i*2*fontsize
							lly=self.center_y+yr-200-rowextra+(j+1)*3*fontsize
						else:
							llx=self.center_x-xr+200+colextra-(colnum-i)*2*fontsize
							lly=self.center_y+yr-200-rowextra+(j+1)*3*fontsize
						c=textblock[j][i]
						if c!=' ':
							if fontsize>30:
								sp=10
							else:
								sp=7
							self.typeletter(textblock[j][i],llx,lly,2*fontsize,3*fontsize,speed=sp)
							time.sleep(0.05)
				colcount+=colnum
				ulx = ulx + colnum*2*fontsize
				if colcount>=coltot:
					break
				colextra=segw%(2*fontsize)
				if flag==1:
					xr = self.probe('right',sz=psz)
				else:
					xr = self.probe('left',sz=psz)
			rowcount += rownum
			rowextra=segh%(3*fontsize)
			xr=400-xr+colextra-colnum*2*fontsize
			uly = uly + rownum*3*fontsize
			if rowcount>=rowtot-1:
				break
			yr = self.probe('down',sz=psz)

	def plotcurve(self):
		a,b = self.center_x, self.center_y
		print('Choose color:\n 1. rainbow\n 2. monochrome\n 3. random noise\n 4. costomized')
		while True:
			color_plan=getch().decode()
			if color_plan in '1234\n\r':
				break
		if color_plan in '4\n\r':
			color_plan='4'
			while True:
				color_string = input('Input your colors in RGB, separate by comma: ').split(',')
				if len(color_string) != 6:
					print('Please input 6 integers between 0-255')
					continue
				break
			r1,g1,b1,r2,g2,b2 = [int(colrgb)%256 for colrgb in color_string]
			print(r1,g1,b1,r2,g2,b2)
		elif color_plan=='2':
			r1,g1,b1,r2,g2,b2 = 0,0,0,255,255,255
		color_period = input('Color phase (press enter for default): ').split(',')
		cp = [0,1,0,0]
		for i in range(len(color_period)):
			try:
				cp[i]=float(color_period[i])
			except:
				pass
		print('Choose the type of curve')
		print(' 0. spiral(clockwise)\n 1. spiral(counterclockwise)\n 2. circle\n 3. hyperbola-I\n 4. hyperbola-II\n 5. hyperbola-III\n 6. spinograph')
		while True:
			curve_type=getch().decode()
			if curve_type in '0123456':
				break
		if curve_type in '016':
			c=input('Number of loops: ')
			try:
				lpn = float(c)
			except:
				lpn = 1
		if curve_type == '6':
			c=input('Parameter k= ')
			try:
				k = float(c)
			except:
				k = 0.5
			c=input('Parameter l= ')
			try:
				l = float(c)
			except:
				l = 1
		interval = input('Input an interval, press enter for default: [0,1]').split(',')
		try:
			left = float(interval[0])
		except:
			left=0
		try:
			right = float(interval[1])
		except:
			right=1
		num_c = input('Number of curves: ')
		try:
			num=int(num_c)
		except:
			num=1
		for n in range(num):
			ratio = n/num
			t = left + ratio*(right-left)
			col_ind = cp[0]+cp[1]*ratio+cp[2]*ratio*ratio+cp[3]*math.sqrt(ratio)
			if color_plan==1:
				color_ratio=col_ind%1
			else:
				col_ratio = 1-abs(col_ind%2-1)
			if color_plan=='1':
				self.setcolor(color_ratio,0,0,rainbow=True)
			elif color_plan=='2':
				self.setcolor(col_ratio*255,col_ratio*255,col_ratio*255)
			elif color_plan=='3':
				self.setcolor(random.randint(0,255),random.randint(0,255),random.randint(0,255))
			elif color_plan=='4':
				self.setcolor(r1*(1-col_ratio)+r2*col_ratio,g1*(1-col_ratio)+g2*col_ratio,b1*(1-col_ratio)+b2*col_ratio)
			if curve_type=='0':
				self.polar(lambda x: 50*(x-2*math.pi*t)/abs(lpn), start=2*math.pi*t, loop=lpn, dir=1)
			elif curve_type=='1':
				self.polar(lambda x: 50*(x-2*math.pi*t)/abs(lpn), start=2*math.pi*t, loop=lpn, dir=-1)
			elif curve_type=='2':
				self.polar(lambda x: 300*(t+0.01), cx=a, cy=b)
			elif curve_type=='3':
				R = 280
				r = 0.6*R*t+10
				theta = math.asin(math.sqrt((R*R-r*r)/(R*R+r*r*t*t)))
				self.paraplot(lambda x: r/math.cos(x), lambda y: t*r*math.tan(y), start=-theta,end=theta)
				self.paraplot(lambda x: t*r*math.tan(x), lambda y: r/math.cos(y), start=-theta,end=theta)
				self.paraplot(lambda x: -r/math.cos(x), lambda y: t*r*math.tan(y), start=-theta,end=theta)
				self.paraplot(lambda x: t*r*math.tan(x), lambda y: -r/math.cos(y), start=-theta,end=theta)
			elif curve_type=='4':
				R = 280
				r = R*(1-t)**0.9
				theta = math.asin(math.sqrt((R*R-r*r)/(R*R+r*r*t*t)))
				self.paraplot(lambda x: r/math.cos(x), lambda y: t*r*math.tan(y), start=-theta,end=theta)
				self.paraplot(lambda x: t*r*math.tan(x), lambda y: r/math.cos(y), start=-theta,end=theta)
				self.paraplot(lambda x: -r/math.cos(x), lambda y: t*r*math.tan(y), start=-theta,end=theta)
				self.paraplot(lambda x: t*r*math.tan(x), lambda y: -r/math.cos(y), start=-theta,end=theta)
			elif curve_type=='5':
				R = 280
				r=R*(1-t)
				theta = math.asin(math.sqrt((R*R-r*r)/(R*R+r*r)))
				self.paraplot(lambda x: r/math.cos(x), lambda y: r*math.tan(y), start=-theta,end=theta)
				self.paraplot(lambda x: r*math.tan(x), lambda y: r/math.cos(y), start=-theta,end=theta)
				self.paraplot(lambda x: -r/math.cos(x), lambda y: r*math.tan(y), start=-theta,end=theta)
				self.paraplot(lambda x: r*math.tan(x), lambda y: -r/math.cos(y), start=-theta,end=theta)
			elif curve_type=='6':
				self.paraplot(lambda x: 100*(t+1)*((1-k)*math.cos(x)+l*k*math.cos((1-k)*x/k))/(1-k+l*k), 
				lambda y: 100*(t+1)*((1-k)*math.sin(y)-l*k*math.sin((1-k)*y/k))/(1-k+l*k), start=0, end=lpn*2*math.pi)
		self.mouse.move(a,b)

	def autospam(self,target,mode):
		a,b = self.center_x, self.center_y
		self.mouse.move(1,100)
		time.sleep(2)
		im=grab()
		pix=[[0 for i in range(22)]for j in range(22)]
		tot=0
		for j in range(220):
			for i in range(220):
				x=a-220+i*2
				y=b-220+j*2
				r0,g0,b0 = im.getpixel((x,y))
				for colors in target:
					r1,g1,b1=colors
					if max(abs(r0-r1),abs(g0-g1),abs(b0-b1))<40:
						pix[j//10][i//10]+=1
						tot+=1
		if tot<3000:
			return 0
		for j in range(22):
			for i in range(22):
				if pix[j][i]>10:
					pix[j][i]=1
				else:
					pix[j][i]=0
		maxsize=0
		bestx,besty=0,0
		width,height=0,0
		if mode==1:
			aux=[[0 for i in range(22)]for j in range(22)]
			for j in range(22):
				aux[0][j]=pix[0][j]
				aux[j][0]=pix[j][0]
			for j in range(1,22):
				for i in range(1,22):
					if pix[j][i]==1:
						sz=min(aux[j-1][i],aux[j][i-1],aux[j-1][i-1])+1
						aux[j][i]=sz
						if sz>maxsize:
							maxsize,width,height=sz,sz,sz
							bestx,besty=i,j
		else:
			aux=[[[0 for k in range(j+1)] for i in range(22)]for j in range(22)]
			aux[0][0][0]=pix[0][0]
			for j in range(1,22):
				if pix[0][j]==1:
					aux[0][j][0]=aux[0][j-1][0]+1
			for j in range(1,22):
				if pix[j][0]==1:
					aux[j][0][0]=1
					for k in range(1,j):
						aux[j][0][k]=aux[j-1][0][k-1]
			for j in range(1,22):
				for i in range(1,22):
					if pix[j][i]==1:
						aux[j][i][0]=aux[j][i-1][0]+1
						for k in range(1,j):
							aux[j][i][k]=min(aux[j][i-1][k]+1,aux[j-1][i][k-1])
							sz=(k+1)*aux[j][i][k]
							if sz>maxsize:
								maxsize=sz
								bestx,besty=i,j
								width,height=aux[j][i][k],k+1
							elif sz==maxsize:
								if abs(aux[j][i][k]-k-1)<abs(width-height):
									bestx,besty=i,j
									width,height=aux[j][i][k],k+1
		if width<=4 or height<=4:
			return 0
		lx=bestx-width+1
		ly=besty-height+1
		cx = a-220+10*(2*lx+width)
		cy = b-220+10*(2*ly+height)
		radiusx = 10*width - 20
		radiusy = 10*height - 20
		if mode==1:
			n=random.randint(4,8)
			theta=random.randint(0,360)
			radius=min(radiusx,radiusy)
			for i in range(2*n+1):
				angle=math.pi*theta/180
				x0=cx+int(radius*math.cos(angle))
				y0=cy+int(radius*math.sin(angle))
				theta+=360*n/(2*n+1)
				angle=math.pi*theta/180
				x1=cx+int(radius*math.cos(angle))
				y1=cy+int(radius*math.sin(angle))
				self.drawline(x0,y0,x1,y1)
		elif mode==2:
			for j in range(cy-radiusy,cy+radiusy,4):
				self.drawline(cx-radiusx,j,cx+radiusx,j)
				#time.sleep(0.1)
		return 1

	def MeteorShower(self):
		h_c=0
		v_c=0
		target = []
		print('What would you like to spam?\n 1. Stars\n 2. Lines')
		c=keyboardinput('12')
		m=int(c)
		print('How many spams per column(default is 20)?')
		c=input()
		try:
			num=int(c)
		except:
			num=20
		print('Input the target color, (use rgb values, e.g. 255,0,0), press enter for default(red and pink).')
		while True:
			try:
				r,g,b=input().split(',')
				r=int(r)
				g=int(g)
				b=int(b)
				target.append((r,g,b))
				print('Color: ',(r,g,b), "included. Press 'a' to add another color, press enter to initiate meteor strike.")
			except:
				break
		if target==[]:
			target=[(250,15,225),(250,0,0)]
		print('Input your color, default is white.')
		try:
			r,g,b=input().split(',')
			r=int(r)%255
			g=int(g)%255
			b=int(b)%255
			self.setcolor(r,g,b)
		except:
			self.setcolor(255,255,255)
		a=0
		while True:
			v_c+=1
			a+=self.autospam(target,mode=m)
			time.sleep(1)
			if v_c == num:
				v_c=0
				h_c+=1
				if h_c>40:
					break
				self.shift('right',1.4)
			elif h_c%2 == 0:
				self.shift('down',1.2)
			else:
				self.shift('up',1.2)
			time.sleep(1)
			print(a,'spammed')
		
	def colortest(self):
		for i in range(63):
			self.mouse.click(self.wheel_x-31+i,self.wheel_y)
			for j in range(-3,4):
				self.drawline(self.center_x+j,self.center_y-3,self.center_x+j,self.center_y+3)
			self.mouse.move(1,100)
			time.sleep(0.2)
			im=grab()
			r,g,b=im.getpixel((self.center_x,self.center_y))
			print(i,r,g,b)
			time.sleep(0.3)

#main
m=PyMouse()
pen = paint(m)
while True:
	system('cls')
	print('*'*20)
	print('   PigScript v1.8   ')
	print('*'*20)
	print(' 1. Draw a local picture\n 2. Draw a website picture\n 3. Draw curves\n 4. Meteor Shower \n 5. Print text\n 6. Exit')
	c=keyboardinput('123456')
	source=int(c)
	if source==6:
		system('cls')
		break
	elif source==5:
		print('----------\n 1. Print text\n 2. Print file')
		c=keyboardinput('12')
		if c=='1':
			w=input('Enter text: ')
			t=[w]
		else:
			fn=input('Enter filename: ')
			t=open(fn).read().replace('\t','    ').split('\n')
		c=input('Enter font size(interger between 3-100, default is 7, greater is larger): ')
		try:
			sz=int(float(c))
			if sz<3:
				sz=3
			elif sz>100:
				sz=100
		except:
			sz=7
		pen.autowrite(t,sz)
		input('Finished, press enter to continue')
		continue
	elif source==4:
		pen.MeteorShower()
	elif source==3:
		pen.plotcurve()
		continue
	elif source==2:
		filename = input('URL of the picture: ')
	else:
		filename = input('Picture name: ')
	print('Enter your pen size (1-9): ')
	while True:
		c=getch().decode()
		if c in '0123456789':
			break
	sc = int(c)
	print('Please manually set your pen size to', c)
	tm = time.clock()
	pen.autodraw(filename, source, sc)
	sec = int(time.clock()-tm)
	print('Time elapsed {} minutes {} seconds'.format(sec//60, sec%60))
	input()
