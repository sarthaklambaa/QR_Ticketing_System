import qrcode
data = 'https"//www.sarthaklamba.in'
img = qrcode.make(data)
img.save("sarthak.png")