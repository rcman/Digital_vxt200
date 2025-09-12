infoserver.zip is an archive of CD images for infoserver software that ran on VAXen under VMS. The infoserver software did some things that helped the VXT2000 do it's job, 
<br>
like provide swap space for the VXT over the network connection, provide fonts, etc. The infoserver software does more than just that, but that's the connection to the VXT2000. There were also specific appliance-style <BR>
infoservers from DEC, which were less multi-purpose.<BR>

<BR>
Here is source for mopd which should build fine on linux. There are some instructions on how to use mopd in there, specifically for booting BSD on a VAX, but they apply similarly for the VXT2000 and booting a VXT software image.<BR>

EDIT3: MOP booting info is here, you can ignore everything except the stuff DIRECTLY related to MOP.<BR>

https://github.com/qu1j0t3/mopd/blob/master/HOWTO-MicroVAX-II.md<BR>

the other stuff is only needed for booting BSD (tftpd, NFS, etc.). It should be noted that you need to put your NIC in promiscuous mode for mopd to work. on linux, for example:<BR>

ifconfig eth0 promisc<BR>

as root.<BR>
<BR>
boot images for MOP go into /tftpboot/mop by default. Rename to <MAC ADDR>.SYS for autoboot typically. Use the MAC address of the device booting from the server, of course. Otherwise, there's usually a way to specify the <BR>
file to boot. Only one MOP boot server can exist on the network at one time, I think. MOP is not routable IP traffic, so your server has to be on the same side of any routers as your booting device.<BR>



<BR>
From this link

<BR>
https://www.reddit.com/r/vintagecomputing/comments/4zj082/comment/db0kvnf/
