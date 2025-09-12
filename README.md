# Digital VXT2000 Notes

<BR><BR>

![vxt-frontback](https://github.com/user-attachments/assets/4e503bd6-7720-40f8-9c30-4a5fb9ec323d)


<BR><BR>


![DEC_VXT2000+_rear_connectors](https://github.com/user-attachments/assets/13b936c3-89fd-4d66-a64b-da4ec4e1fca3)

<BR><BR>


Dec Digital 3W3 bnc rgb cable

 You need a video cable with a 3W3 connector on one end. Original was likely a DEC BC29G-10.
That, plus 5BNC-to-VGA cables, and 3 F/F BNC barrels, will work with a multisync monitor that handles sync-on-green.

https://www.vaxarchive.org/hardware/cables.html

IBM 3W3 Adapter to 3 BNC RGB Video Cable


BC29G-10  10ft cable<BR>
BC29G-09	Colour Monitor Cable 9ft	100.00<BR>
BC29G-12	Colour Monitor Cable 12ft 100.00<BR>

<BR>
http://www.cablesforcomputers.com/scrpts/groupsearchLink.pl?search=DEC

<BR>

# IBM cable of same type

<BR><BR>
https://www.worthpoint.com/worthopedia/ibm-3w3-adapter-bnc-rgb-video-cable-4690518977
<BR><BR>
# Another site with these cables

<BR><BR>

https://picclick.com/17-02906-01-Bc29G-09-Dec-9Ft-274M-Rgb-Video-Cable-233724347639.html

<BR><BR>

# MOP Install

<BR><BR>
https://github.com/toadstorm/MOPS/wiki/Installation

<BR><BR>

# Video Cable

<BR><BR>

The VXT uses a delightful plug called 3W3. You might have heard of 13W3, the video connector that appeared on Suns, SGIs, a few IBMs, and other things. Adapters for that are incredibly common, but 3W3... is not so much.<BR>
<BR>
The signal itself is not so exotic; it's just Sync-On-Green RGB, sent over three mini coaxial plugs. From left to right it's Blue, Green, Red. Many LCD monitors and scalers (such as the Extron RGB 300 HDMI) support SoG, and all you need for testing is the green line; simply get it finagled up to the green wire on a VGA cable, some way, somehow, and plug it into a few different LCD monitors; one of them will probably sync. The picture will look awful though unless you can get the ground wire onto the outer half of the coax plug, and this is... quite hard to do in any kind of sustainable way without a proper cable.
<BR>
<BR>
What to do about this? Well, ideally you'd get a 3W3 cable... but they're quite rare. IBM sold them under the FRU "58F22903" and I bought one on ebay by searching for that, but there aren't any others available right now. Searching "3W3" may get you results, but they'll be quite pricey. Are there other options?
<BR>
<BR>
Well, if you're really impatient, you could do what I did: Get a 13W3 adapter (they are INCREDIBLY common and cheap on ebay,) break it apart, extract the mini-coax connectors, and solder them to a VGA cable. This is a huge pain in the ass; you have to slice off the external PVC covering, which is quite thick, then you'll probably find out that it's potted inside.
<BR>
<BR>
Don't give up though; if your potting is milky-white like mine, it's probably hot glue. Hot glue is extremely susceptible to isopropyl alcohol; pour some on there, give it a minute, then use a pair of pliers to break it apart. You'll destroy all the wires; doesn't matter, you're reworking it anyway.
<BR>
<BR>
You'll have to snap the end tab off the 13W3 plug to separate the halves so you can get the plastic wedge out which contains the coax plugs, then cut those out with wire cutters. I told you this was a pain in the ass! It took me 45 minutes! But in the end I had three little coax barrels, which I soldered to a cable, and voila, I had a picture.
<BR>
<BR>
I guess you could also try to find an actual 3W3 plug. They're still sold, there's just 50,000 SKUs on digikey and almost all of them have power pins instead of coax. I found a VCfed post saying these ones worked, but they come from China so you'll be waiting a while.

<BR>


# MOPD

<BR>

https://github.com/dreamlayers/netbsd-mopd

<BR>
https://www.netbsd.org/docs/network/netboot/mop.html#linux
<BR>
https://www.netbsd.org/docs/network/netboot/bootpd.html
<BR>
https://www.netbsd.org/docs/network/netboot/tftpd.html
<BR>
https://www.netbsd.org/docs/network/netboot/nfs.html
<BR>

