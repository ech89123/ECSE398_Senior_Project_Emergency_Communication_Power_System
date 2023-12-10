import I2C_LCD_driver
import socket
import fcntl
import struct
import time

mylcd = I2C_LCD_driver.lcd()

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,struct.pack('256s',bytes(ifname[:15],'utf-8')))[20:24])    
	

def printIP():
	for num in reversed(range(31)): 
		mylcd.lcd_clear()
		mylcd.lcd_display_string("IP Printed in: " + str(num), 2)
		time.sleep(1) 
		
	try:
		ip = get_ip_address('eth0') 
		mylcd.lcd_clear()
		mylcd.lcd_display_string("Wired", 1) 
		mylcd.lcd_display_string("IP Address:", 2) 
		mylcd.lcd_display_string(ip, 3)

	except:
		try:
			ip = get_ip_address('wlan0')
			mylcd.lcd_clear()
			mylcd.lcd_display_string("Wireless", 1) 
			mylcd.lcd_display_string("IP Address:", 2) 
			mylcd.lcd_display_string(ip, 3)

		
		except:
			mylcd.lcd_display_string("NO CONNECTIVITY", 2)
			
			
printIP()
