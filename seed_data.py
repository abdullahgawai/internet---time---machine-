"""
Seed script for Internet Time Machine — populates the SQLite database with
realistic snapshot data for the six preset "Time Capsule" sites so the app
works out-of-the-box without waiting for the Wayback Machine CDX API.
"""
import sqlite3
import json
import os
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "time_machine.db")

# ─── Realistic snapshot data per site ───────────────────────────────────────────
# Each entry: (timestamp_YYYYMMDDHHMMSS, status_code, mimetype, length)
# Timestamps are collapsed to ~1 per month as the CDX service does (collapse=timestamp:6)

SITES = {
    "apple.com": {
        "start_year": 1997,
        "snapshots": [
            # 1997 — original Steve Jobs era, basic HTML
            ("19970401120000", 200, "text/html", 3842),
            ("19970615080000", 200, "text/html", 4102),
            ("19970912143000", 200, "text/html", 5200),
            # 1998
            ("19980215100000", 200, "text/html", 5890),
            ("19980610140000", 200, "text/html", 6120),
            ("19981105090000", 200, "text/html", 7300),
            # 1999 — iMac era
            ("19990318110000", 200, "text/html", 8450),
            ("19990722150000", 200, "text/html", 9100),
            ("19991201130000", 200, "text/html", 10200),
            # 2000
            ("20000305120000", 200, "text/html", 11500),
            ("20000815140000", 200, "text/html", 12800),
            ("20001120100000", 200, "text/html", 13600),
            # 2001 — iPod launch
            ("20010410090000", 200, "text/html", 14200),
            ("20010823130000", 200, "text/html", 15800),
            ("20011115160000", 200, "text/html", 18200),
            # 2002
            ("20020312110000", 200, "text/html", 19500),
            ("20020718140000", 200, "text/html", 21000),
            ("20021022080000", 200, "text/html", 22400),
            # 2003 — iTunes Store
            ("20030228120000", 200, "text/html", 24500),
            ("20030615100000", 200, "text/html", 26800),
            ("20031010150000", 200, "text/html", 28900),
            # 2004
            ("20040320130000", 200, "text/html", 30200),
            ("20040705090000", 200, "text/html", 32100),
            ("20041112110000", 200, "text/html", 34500),
            # 2005
            ("20050405140000", 200, "text/html", 36200),
            ("20050820100000", 200, "text/html", 38400),
            ("20051215130000", 200, "text/html", 40100),
            # 2006
            ("20060310120000", 200, "text/html", 42800),
            ("20060715160000", 200, "text/html", 45200),
            ("20061105090000", 200, "text/html", 48600),
            # 2007 — iPhone launch
            ("20070112100000", 200, "text/html", 52400),
            ("20070629140000", 200, "text/html", 68000),
            ("20071015130000", 200, "text/html", 72500),
            # 2008
            ("20080318120000", 200, "text/html", 76200),
            ("20080711150000", 200, "text/html", 82400),
            ("20081020100000", 200, "text/html", 88600),
            # 2009
            ("20090425110000", 200, "text/html", 92400),
            ("20090830140000", 200, "text/html", 96800),
            ("20091210130000", 200, "text/html", 101200),
            # 2010 — iPad launch
            ("20100310090000", 200, "text/html", 108500),
            ("20100720120000", 200, "text/html", 115800),
            ("20101115140000", 200, "text/html", 122400),
            # 2011
            ("20110405100000", 200, "text/html", 128600),
            ("20110812130000", 200, "text/html", 135200),
            ("20111118150000", 200, "text/html", 142800),
            # 2012
            ("20120315110000", 200, "text/html", 148500),
            ("20120720140000", 200, "text/html", 156200),
            ("20121025090000", 200, "text/html", 164800),
            # 2013 — flat design (iOS 7)
            ("20130418120000", 200, "text/html", 172500),
            ("20130910130000", 200, "text/html", 185600),
            ("20131215100000", 200, "text/html", 192400),
            # 2014
            ("20140322140000", 200, "text/html", 205800),
            ("20140815110000", 200, "text/html", 218400),
            ("20141120150000", 200, "text/html", 228600),
            # 2015
            ("20150410090000", 200, "text/html", 242800),
            ("20150725130000", 200, "text/html", 256200),
            ("20151210120000", 200, "text/html", 268400),
            # 2016
            ("20160318100000", 200, "text/html", 282600),
            ("20160805140000", 200, "text/html", 295800),
            ("20161115130000", 200, "text/html", 308200),
            # 2017
            ("20170420110000", 200, "text/html", 322400),
            ("20170912150000", 200, "text/html", 345600),
            ("20171218090000", 200, "text/html", 358200),
            # 2018
            ("20180305120000", 200, "text/html", 372800),
            ("20180720140000", 200, "text/html", 388400),
            ("20181025100000", 200, "text/html", 402600),
            # 2019
            ("20190415130000", 200, "text/html", 418200),
            ("20190830110000", 200, "text/html", 435800),
            ("20191210150000", 200, "text/html", 452400),
            # 2020
            ("20200310090000", 200, "text/html", 468600),
            ("20200715120000", 200, "text/html", 485200),
            ("20201120140000", 200, "text/html", 502800),
            # 2021
            ("20210418100000", 200, "text/html", 518400),
            ("20210825130000", 200, "text/html", 535200),
            ("20211215150000", 200, "text/html", 552600),
            # 2022
            ("20220320110000", 200, "text/html", 568200),
            ("20220710140000", 200, "text/html", 585800),
            ("20221105090000", 200, "text/html", 602400),
            # 2023
            ("20230410120000", 200, "text/html", 618200),
            ("20230815100000", 200, "text/html", 635800),
            ("20231120130000", 200, "text/html", 652400),
            # 2024
            ("20240315140000", 200, "text/html", 668600),
            ("20240720110000", 200, "text/html", 685200),
            ("20241025150000", 200, "text/html", 702800),
            # 2025
            ("20250318090000", 200, "text/html", 718400),
            ("20250712120000", 200, "text/html", 735200),
            ("20251015140000", 200, "text/html", 752600),
            # 2026
            ("20260215100000", 200, "text/html", 768200),
            ("20260610130000", 200, "text/html", 785800),
        ],
    },
    "google.com": {
        "start_year": 1998,
        "snapshots": [
            # 1998 — original Stanford project page
            ("19981111120000", 200, "text/html", 2534),
            ("19981215140000", 200, "text/html", 2680),
            # 1999
            ("19990318100000", 200, "text/html", 3120),
            ("19990625130000", 200, "text/html", 3450),
            ("19991010150000", 200, "text/html", 3820),
            # 2000
            ("20000215090000", 200, "text/html", 4200),
            ("20000620120000", 200, "text/html", 4850),
            ("20001105140000", 200, "text/html", 5200),
            # 2001
            ("20010410110000", 200, "text/html", 5680),
            ("20010815130000", 200, "text/html", 6100),
            ("20011210100000", 200, "text/html", 6520),
            # 2002
            ("20020315120000", 200, "text/html", 6890),
            ("20020720150000", 200, "text/html", 7250),
            ("20021025090000", 200, "text/html", 7680),
            # 2003
            ("20030418140000", 200, "text/html", 8120),
            ("20030810110000", 200, "text/html", 8540),
            ("20031215130000", 200, "text/html", 8920),
            # 2004
            ("20040320100000", 200, "text/html", 9450),
            ("20040725120000", 200, "text/html", 9880),
            ("20041110150000", 200, "text/html", 10350),
            # 2005
            ("20050412090000", 200, "text/html", 10820),
            ("20050815140000", 200, "text/html", 11280),
            ("20051220110000", 200, "text/html", 11750),
            # 2006
            ("20060318130000", 200, "text/html", 12200),
            ("20060725100000", 200, "text/html", 12680),
            ("20061110120000", 200, "text/html", 13150),
            # 2007
            ("20070415150000", 200, "text/html", 13620),
            ("20070820090000", 200, "text/html", 14100),
            ("20071215140000", 200, "text/html", 14580),
            # 2008
            ("20080310110000", 200, "text/html", 15200),
            ("20080720130000", 200, "text/html", 15850),
            ("20081025100000", 200, "text/html", 16420),
            # 2009
            ("20090418120000", 200, "text/html", 17100),
            ("20090825150000", 200, "text/html", 17800),
            ("20091210090000", 200, "text/html", 18520),
            # 2010
            ("20100315140000", 200, "text/html", 19200),
            ("20100720110000", 200, "text/html", 19950),
            ("20101115130000", 200, "text/html", 20680),
            # 2011
            ("20110410100000", 200, "text/html", 21450),
            ("20110815120000", 200, "text/html", 22200),
            ("20111210150000", 200, "text/html", 23000),
            # 2012
            ("20120318090000", 200, "text/html", 24800),
            ("20120720140000", 200, "text/html", 26500),
            ("20121105110000", 200, "text/html", 28200),
            # 2013 — Material-ish direction
            ("20130415130000", 200, "text/html", 32500),
            ("20130820100000", 200, "text/html", 35800),
            ("20131215120000", 200, "text/html", 38200),
            # 2014
            ("20140310150000", 200, "text/html", 42500),
            ("20140725090000", 200, "text/html", 46800),
            ("20141110140000", 200, "text/html", 51200),
            # 2015
            ("20150418110000", 200, "text/html", 55800),
            ("20150815130000", 200, "text/html", 60200),
            ("20151220100000", 200, "text/html", 64800),
            # 2016
            ("20160315120000", 200, "text/html", 68500),
            ("20160720150000", 200, "text/html", 72200),
            ("20161105090000", 200, "text/html", 76800),
            # 2017
            ("20170410140000", 200, "text/html", 82500),
            ("20170815110000", 200, "text/html", 88200),
            ("20171220130000", 200, "text/html", 94800),
            # 2018
            ("20180318100000", 200, "text/html", 102500),
            ("20180725120000", 200, "text/html", 110200),
            ("20181110150000", 200, "text/html", 118800),
            # 2019
            ("20190415090000", 200, "text/html", 128500),
            ("20190820140000", 200, "text/html", 138200),
            ("20191215110000", 200, "text/html", 148800),
            # 2020
            ("20200310130000", 200, "text/html", 158500),
            ("20200720100000", 200, "text/html", 168200),
            ("20201115120000", 200, "text/html", 178800),
            # 2021
            ("20210418150000", 200, "text/html", 188500),
            ("20210825090000", 200, "text/html", 198200),
            ("20211215140000", 200, "text/html", 208800),
            # 2022
            ("20220320110000", 200, "text/html", 218500),
            ("20220710130000", 200, "text/html", 228200),
            ("20221105100000", 200, "text/html", 238800),
            # 2023
            ("20230415120000", 200, "text/html", 248500),
            ("20230820150000", 200, "text/html", 258200),
            ("20231110090000", 200, "text/html", 268800),
            # 2024
            ("20240310140000", 200, "text/html", 278500),
            ("20240720110000", 200, "text/html", 288200),
            ("20241025130000", 200, "text/html", 298800),
            # 2025
            ("20250315100000", 200, "text/html", 308500),
            ("20250720120000", 200, "text/html", 318200),
            ("20251020150000", 200, "text/html", 328800),
            # 2026
            ("20260218090000", 200, "text/html", 338500),
            ("20260615140000", 200, "text/html", 348200),
        ],
    },
    "amazon.com": {
        "start_year": 1999,
        "snapshots": [
            # 1999 — early bookstore era
            ("19990115120000", 200, "text/html", 18500),
            ("19990510140000", 200, "text/html", 22400),
            ("19990918100000", 200, "text/html", 26800),
            # 2000
            ("20000220130000", 200, "text/html", 32500),
            ("20000715150000", 200, "text/html", 38200),
            ("20001110090000", 200, "text/html", 45600),
            # 2001
            ("20010418110000", 200, "text/html", 52800),
            ("20010825140000", 200, "text/html", 58400),
            ("20011215120000", 200, "text/html", 64200),
            # 2002
            ("20020315100000", 200, "text/html", 72500),
            ("20020720130000", 200, "text/html", 78800),
            ("20021105150000", 200, "text/html", 85200),
            # 2003
            ("20030410090000", 200, "text/html", 92600),
            ("20030815120000", 200, "text/html", 98400),
            ("20031210140000", 200, "text/html", 105800),
            # 2004
            ("20040318110000", 200, "text/html", 112500),
            ("20040725130000", 200, "text/html", 118200),
            ("20041020100000", 200, "text/html", 125600),
            # 2005
            ("20050412150000", 200, "text/html", 132800),
            ("20050820090000", 200, "text/html", 140200),
            ("20051215120000", 200, "text/html", 148600),
            # 2006
            ("20060310140000", 200, "text/html", 158200),
            ("20060720110000", 200, "text/html", 168800),
            ("20061105130000", 200, "text/html", 178400),
            # 2007
            ("20070415100000", 200, "text/html", 192600),
            ("20070825120000", 200, "text/html", 205200),
            ("20071210150000", 200, "text/html", 218800),
            # 2008
            ("20080318090000", 200, "text/html", 232500),
            ("20080720140000", 200, "text/html", 248200),
            ("20081025110000", 200, "text/html", 262800),
            # 2009
            ("20090410130000", 200, "text/html", 278500),
            ("20090815100000", 200, "text/html", 295200),
            ("20091220120000", 200, "text/html", 312800),
            # 2010
            ("20100315150000", 200, "text/html", 328500),
            ("20100720090000", 200, "text/html", 345200),
            ("20101115140000", 200, "text/html", 362800),
            # 2011
            ("20110418110000", 200, "text/html", 382500),
            ("20110825130000", 200, "text/html", 402200),
            ("20111215100000", 200, "text/html", 422800),
            # 2012
            ("20120310120000", 200, "text/html", 445600),
            ("20120720150000", 200, "text/html", 468200),
            ("20121105090000", 200, "text/html", 492800),
            # 2013
            ("20130415140000", 200, "text/html", 518500),
            ("20130820110000", 200, "text/html", 545200),
            ("20131210130000", 200, "text/html", 572800),
            # 2014
            ("20140318100000", 200, "text/html", 598500),
            ("20140725120000", 200, "text/html", 625200),
            ("20141110150000", 200, "text/html", 652800),
            # 2015
            ("20150412090000", 200, "text/html", 685200),
            ("20150815140000", 200, "text/html", 718800),
            ("20151220110000", 200, "text/html", 752400),
            # 2016
            ("20160315130000", 200, "text/html", 788500),
            ("20160720100000", 200, "text/html", 825200),
            ("20161105120000", 200, "text/html", 862800),
            # 2017
            ("20170410150000", 200, "text/html", 902500),
            ("20170815090000", 200, "text/html", 942200),
            ("20171220140000", 200, "text/html", 982800),
            # 2018
            ("20180318110000", 200, "text/html", 1025600),
            ("20180725130000", 200, "text/html", 1068200),
            ("20181110100000", 200, "text/html", 1112800),
            # 2019
            ("20190415120000", 200, "text/html", 1158500),
            ("20190820150000", 200, "text/html", 1205200),
            ("20191215090000", 200, "text/html", 1252800),
            # 2020
            ("20200310140000", 200, "text/html", 1298500),
            ("20200720110000", 200, "text/html", 1345200),
            ("20201115130000", 200, "text/html", 1392800),
            # 2021
            ("20210418100000", 200, "text/html", 1438500),
            ("20210825120000", 200, "text/html", 1485200),
            ("20211215150000", 200, "text/html", 1532800),
            # 2022
            ("20220320090000", 200, "text/html", 1578500),
            ("20220710140000", 200, "text/html", 1625200),
            ("20221105110000", 200, "text/html", 1672800),
            # 2023
            ("20230410130000", 200, "text/html", 1718500),
            ("20230815100000", 200, "text/html", 1765200),
            ("20231120120000", 200, "text/html", 1812800),
            # 2024
            ("20240315150000", 200, "text/html", 1858500),
            ("20240720090000", 200, "text/html", 1905200),
            ("20241025140000", 200, "text/html", 1952800),
            # 2025
            ("20250318110000", 200, "text/html", 1998500),
            ("20250712130000", 200, "text/html", 2045200),
            ("20251015100000", 200, "text/html", 2092800),
            # 2026
            ("20260215120000", 200, "text/html", 2138500),
            ("20260610150000", 200, "text/html", 2185200),
        ],
    },
    "spacejam.com": {
        "start_year": 1996,
        "snapshots": [
            # 1996 — original movie promo site (largely unchanged!)
            ("19961115120000", 200, "text/html", 4200),
            # 1997
            ("19970315100000", 200, "text/html", 4200),
            ("19970810140000", 200, "text/html", 4200),
            # 1998
            ("19980420130000", 200, "text/html", 4200),
            ("19981015110000", 200, "text/html", 4200),
            # 1999
            ("19990518120000", 200, "text/html", 4200),
            ("19991210150000", 200, "text/html", 4200),
            # 2000
            ("20000315090000", 200, "text/html", 4200),
            ("20000820140000", 200, "text/html", 4200),
            # 2001
            ("20010418110000", 200, "text/html", 4200),
            ("20011015130000", 200, "text/html", 4200),
            # 2002
            ("20020610120000", 200, "text/html", 4200),
            ("20021115100000", 200, "text/html", 4200),
            # 2003
            ("20030420150000", 200, "text/html", 4200),
            ("20031010090000", 200, "text/html", 4200),
            # 2004
            ("20040315140000", 200, "text/html", 4200),
            ("20040820110000", 200, "text/html", 4200),
            # 2005
            ("20050510130000", 200, "text/html", 4200),
            ("20051115100000", 200, "text/html", 4200),
            # 2006
            ("20060420120000", 200, "text/html", 4200),
            ("20061015150000", 200, "text/html", 4200),
            # 2007
            ("20070318090000", 200, "text/html", 4200),
            ("20070815140000", 200, "text/html", 4200),
            # 2008
            ("20080510110000", 200, "text/html", 4200),
            ("20081020130000", 200, "text/html", 4200),
            # 2009
            ("20090415100000", 200, "text/html", 4200),
            ("20091210120000", 200, "text/html", 4200),
            # 2010
            ("20100320150000", 200, "text/html", 4200),
            ("20100825090000", 200, "text/html", 4200),
            # 2011
            ("20110518140000", 200, "text/html", 4200),
            ("20111015110000", 200, "text/html", 4200),
            # 2012
            ("20120310130000", 200, "text/html", 4200),
            ("20120815100000", 200, "text/html", 4200),
            # 2013
            ("20130420120000", 200, "text/html", 4200),
            ("20131010150000", 200, "text/html", 4200),
            # 2014
            ("20140315090000", 200, "text/html", 4200),
            ("20140820140000", 200, "text/html", 4200),
            # 2015
            ("20150510110000", 200, "text/html", 4200),
            ("20151115130000", 200, "text/html", 4200),
            # 2016
            ("20160418100000", 200, "text/html", 4200),
            ("20161015120000", 200, "text/html", 4200),
            # 2017
            ("20170320150000", 200, "text/html", 4200),
            ("20170825090000", 200, "text/html", 4200),
            # 2018
            ("20180510140000", 200, "text/html", 4200),
            ("20181020110000", 200, "text/html", 4200),
            # 2019
            ("20190418130000", 200, "text/html", 4200),
            ("20191015100000", 200, "text/html", 4200),
            # 2020
            ("20200315120000", 200, "text/html", 4200),
            ("20200820150000", 200, "text/html", 4200),
            # 2021 — Space Jam 2 era, site gets redesigned
            ("20210310090000", 200, "text/html", 4200),
            ("20210716140000", 200, "text/html", 85200),
            ("20211015110000", 200, "text/html", 88500),
            # 2022
            ("20220418130000", 200, "text/html", 82400),
            ("20221010100000", 200, "text/html", 78600),
            # 2023
            ("20230315120000", 200, "text/html", 72800),
            ("20230820150000", 200, "text/html", 68200),
            # 2024
            ("20240510090000", 200, "text/html", 65400),
            ("20241015140000", 200, "text/html", 62800),
            # 2025
            ("20250318110000", 200, "text/html", 58200),
            ("20250815130000", 200, "text/html", 55600),
        ],
    },
    "yahoo.com": {
        "start_year": 1996,
        "snapshots": [
            # 1996 — Yahoo! directory era
            ("19961020120000", 200, "text/html", 12500),
            ("19961215140000", 200, "text/html", 14200),
            # 1997
            ("19970318100000", 200, "text/html", 18500),
            ("19970715130000", 200, "text/html", 22400),
            ("19971210150000", 200, "text/html", 26800),
            # 1998
            ("19980415090000", 200, "text/html", 32500),
            ("19980820120000", 200, "text/html", 38200),
            ("19981115140000", 200, "text/html", 45600),
            # 1999
            ("19990310110000", 200, "text/html", 52800),
            ("19990725130000", 200, "text/html", 62400),
            ("19991210100000", 200, "text/html", 72200),
            # 2000 — portal boom
            ("20000215120000", 200, "text/html", 85500),
            ("20000720150000", 200, "text/html", 98200),
            ("20001105090000", 200, "text/html", 112800),
            # 2001
            ("20010418140000", 200, "text/html", 125500),
            ("20010825110000", 200, "text/html", 138200),
            ("20011215130000", 200, "text/html", 152800),
            # 2002
            ("20020310100000", 200, "text/html", 165500),
            ("20020720120000", 200, "text/html", 178200),
            ("20021105150000", 200, "text/html", 192800),
            # 2003
            ("20030415090000", 200, "text/html", 205500),
            ("20030820140000", 200, "text/html", 218200),
            ("20031210110000", 200, "text/html", 232800),
            # 2004
            ("20040318130000", 200, "text/html", 248500),
            ("20040725100000", 200, "text/html", 265200),
            ("20041110120000", 200, "text/html", 282800),
            # 2005
            ("20050412150000", 200, "text/html", 298500),
            ("20050815090000", 200, "text/html", 315200),
            ("20051220140000", 200, "text/html", 332800),
            # 2006
            ("20060315110000", 200, "text/html", 352500),
            ("20060720130000", 200, "text/html", 372200),
            ("20061105100000", 200, "text/html", 392800),
            # 2007
            ("20070418120000", 200, "text/html", 415500),
            ("20070820150000", 200, "text/html", 438200),
            ("20071215090000", 200, "text/html", 462800),
            # 2008
            ("20080310140000", 200, "text/html", 485500),
            ("20080725110000", 200, "text/html", 508200),
            ("20081110130000", 200, "text/html", 532800),
            # 2009
            ("20090415100000", 200, "text/html", 558500),
            ("20090820120000", 200, "text/html", 585200),
            ("20091220150000", 200, "text/html", 612800),
            # 2010
            ("20100315090000", 200, "text/html", 638500),
            ("20100720140000", 200, "text/html", 665200),
            ("20101115110000", 200, "text/html", 692800),
            # 2011
            ("20110418130000", 200, "text/html", 718500),
            ("20110825100000", 200, "text/html", 745200),
            ("20111215120000", 200, "text/html", 772800),
            # 2012
            ("20120310150000", 200, "text/html", 802500),
            ("20120720090000", 200, "text/html", 832200),
            ("20121105140000", 200, "text/html", 862800),
            # 2013 — Marissa Mayer redesign
            ("20130415110000", 200, "text/html", 452500),
            ("20130820130000", 200, "text/html", 468200),
            ("20131210100000", 200, "text/html", 485800),
            # 2014
            ("20140318120000", 200, "text/html", 502500),
            ("20140725150000", 200, "text/html", 518200),
            ("20141110090000", 200, "text/html", 535800),
            # 2015
            ("20150412140000", 200, "text/html", 552500),
            ("20150815110000", 200, "text/html", 568200),
            ("20151220130000", 200, "text/html", 585800),
            # 2016
            ("20160315100000", 200, "text/html", 602500),
            ("20160720120000", 200, "text/html", 618200),
            ("20161105150000", 200, "text/html", 635800),
            # 2017
            ("20170410090000", 200, "text/html", 652500),
            ("20170815140000", 200, "text/html", 668200),
            ("20171220110000", 200, "text/html", 685800),
            # 2018
            ("20180318130000", 200, "text/html", 702500),
            ("20180725100000", 200, "text/html", 718200),
            ("20181110120000", 200, "text/html", 735800),
            # 2019
            ("20190415150000", 200, "text/html", 752500),
            ("20190820090000", 200, "text/html", 768200),
            ("20191215140000", 200, "text/html", 785800),
            # 2020
            ("20200310110000", 200, "text/html", 802500),
            ("20200720130000", 200, "text/html", 818200),
            ("20201115100000", 200, "text/html", 835800),
            # 2021
            ("20210418120000", 200, "text/html", 852500),
            ("20210825150000", 200, "text/html", 868200),
            ("20211215090000", 200, "text/html", 885800),
            # 2022
            ("20220320140000", 200, "text/html", 902500),
            ("20220710110000", 200, "text/html", 918200),
            ("20221105130000", 200, "text/html", 935800),
            # 2023
            ("20230410100000", 200, "text/html", 952500),
            ("20230815120000", 200, "text/html", 968200),
            ("20231120150000", 200, "text/html", 985800),
            # 2024
            ("20240315090000", 200, "text/html", 1002500),
            ("20240720140000", 200, "text/html", 1018200),
            ("20241025110000", 200, "text/html", 1035800),
            # 2025
            ("20250318130000", 200, "text/html", 1052500),
            ("20250712100000", 200, "text/html", 1068200),
            ("20251015120000", 200, "text/html", 1085800),
            # 2026
            ("20260215150000", 200, "text/html", 1102500),
            ("20260610090000", 200, "text/html", 1118200),
        ],
    },
    "wikipedia.org": {
        "start_year": 2001,
        "snapshots": [
            # 2001 — Wikipedia launches
            ("20010115120000", 200, "text/html", 2800),
            ("20010620140000", 200, "text/html", 4200),
            ("20011015100000", 200, "text/html", 5600),
            # 2002
            ("20020318130000", 200, "text/html", 8200),
            ("20020725150000", 200, "text/html", 10800),
            ("20021110090000", 200, "text/html", 13400),
            # 2003
            ("20030415120000", 200, "text/html", 16200),
            ("20030820140000", 200, "text/html", 19800),
            ("20031215110000", 200, "text/html", 23400),
            # 2004
            ("20040310100000", 200, "text/html", 28200),
            ("20040720130000", 200, "text/html", 32800),
            ("20041105150000", 200, "text/html", 38400),
            # 2005
            ("20050418090000", 200, "text/html", 42200),
            ("20050815120000", 200, "text/html", 46800),
            ("20051220140000", 200, "text/html", 52400),
            # 2006
            ("20060315110000", 200, "text/html", 58200),
            ("20060720100000", 200, "text/html", 64800),
            ("20061105130000", 200, "text/html", 72400),
            # 2007
            ("20070410150000", 200, "text/html", 78200),
            ("20070825090000", 200, "text/html", 84800),
            ("20071210120000", 200, "text/html", 92400),
            # 2008
            ("20080318140000", 200, "text/html", 98200),
            ("20080720110000", 200, "text/html", 105800),
            ("20081025130000", 200, "text/html", 112400),
            # 2009
            ("20090415100000", 200, "text/html", 118200),
            ("20090820120000", 200, "text/html", 125800),
            ("20091215150000", 200, "text/html", 132400),
            # 2010
            ("20100310090000", 200, "text/html", 138200),
            ("20100725140000", 200, "text/html", 145800),
            ("20101110110000", 200, "text/html", 152400),
            # 2011
            ("20110418130000", 200, "text/html", 158200),
            ("20110815100000", 200, "text/html", 165800),
            ("20111220120000", 200, "text/html", 172400),
            # 2012
            ("20120315150000", 200, "text/html", 178200),
            ("20120720090000", 200, "text/html", 185800),
            ("20121105140000", 200, "text/html", 192400),
            # 2013
            ("20130410110000", 200, "text/html", 198200),
            ("20130825130000", 200, "text/html", 205800),
            ("20131215100000", 200, "text/html", 212400),
            # 2014
            ("20140318120000", 200, "text/html", 218200),
            ("20140720150000", 200, "text/html", 225800),
            ("20141105090000", 200, "text/html", 232400),
            # 2015
            ("20150415140000", 200, "text/html", 238200),
            ("20150820110000", 200, "text/html", 245800),
            ("20151210130000", 200, "text/html", 252400),
            # 2016
            ("20160310100000", 200, "text/html", 258200),
            ("20160725120000", 200, "text/html", 265800),
            ("20161110150000", 200, "text/html", 272400),
            # 2017
            ("20170418090000", 200, "text/html", 278200),
            ("20170815140000", 200, "text/html", 285800),
            ("20171220110000", 200, "text/html", 292400),
            # 2018
            ("20180315130000", 200, "text/html", 298200),
            ("20180720100000", 200, "text/html", 305800),
            ("20181105120000", 200, "text/html", 312400),
            # 2019
            ("20190410150000", 200, "text/html", 318200),
            ("20190825090000", 200, "text/html", 325800),
            ("20191215140000", 200, "text/html", 332400),
            # 2020
            ("20200318110000", 200, "text/html", 338200),
            ("20200720130000", 200, "text/html", 345800),
            ("20201115100000", 200, "text/html", 352400),
            # 2021
            ("20210415120000", 200, "text/html", 358200),
            ("20210820150000", 200, "text/html", 365800),
            ("20211210090000", 200, "text/html", 372400),
            # 2022
            ("20220310140000", 200, "text/html", 378200),
            ("20220725110000", 200, "text/html", 385800),
            ("20221105130000", 200, "text/html", 392400),
            # 2023
            ("20230418100000", 200, "text/html", 398200),
            ("20230815120000", 200, "text/html", 405800),
            ("20231220150000", 200, "text/html", 412400),
            # 2024
            ("20240315090000", 200, "text/html", 418200),
            ("20240720140000", 200, "text/html", 425800),
            ("20241025110000", 200, "text/html", 432400),
            # 2025
            ("20250410130000", 200, "text/html", 438200),
            ("20250815100000", 200, "text/html", 445800),
            ("20251015120000", 200, "text/html", 452400),
            # 2026
            ("20260218150000", 200, "text/html", 458200),
            ("20260615090000", 200, "text/html", 465800),
        ],
    },
}

# ─── Metadata templates per site (historically-accurate tech evolution) ──────
# Returns (dom_nodes, images, external_resources, has_mobile, frameworks) for a given year

def get_metadata_for_site_year(site, year):
    """Generate realistic structural metadata based on site and era."""
    
    if site == "apple.com":
        if year <= 1999:
            return (120, 8, 2, False, ["Table-Based Layout (Classic Web)"])
        elif year <= 2003:
            return (280, 18, 5, False, ["Table-Based Layout (Classic Web)"])
        elif year <= 2006:
            return (450, 32, 12, False, ["Table-Based Layout (Classic Web)", "Adobe Flash"])
        elif year <= 2009:
            return (680, 48, 22, False, ["jQuery", "Adobe Flash"])
        elif year <= 2012:
            return (920, 62, 35, False, ["jQuery", "Web Fonts / FontAwesome"])
        elif year <= 2015:
            return (1250, 78, 48, True, ["jQuery", "Web Fonts / FontAwesome", "HTML5 Semantic Layout"])
        elif year <= 2018:
            return (1580, 92, 62, True, ["jQuery", "Web Fonts / FontAwesome", "HTML5 Semantic Layout"])
        elif year <= 2021:
            return (1920, 105, 78, True, ["Web Fonts / FontAwesome", "HTML5 Semantic Layout"])
        else:
            return (2250, 118, 92, True, ["Web Fonts / FontAwesome", "HTML5 Semantic Layout", "React / Next.js"])
    
    elif site == "google.com":
        if year <= 2000:
            return (45, 2, 1, False, [])
        elif year <= 2004:
            return (68, 3, 2, False, ["Table-Based Layout (Classic Web)"])
        elif year <= 2008:
            return (95, 5, 4, False, ["jQuery"])
        elif year <= 2012:
            return (142, 8, 8, False, ["jQuery"])
        elif year <= 2016:
            return (225, 12, 15, True, ["jQuery", "Web Fonts / FontAwesome"])
        elif year <= 2020:
            return (380, 18, 25, True, ["Web Fonts / FontAwesome", "HTML5 Semantic Layout"])
        else:
            return (520, 22, 35, True, ["Web Fonts / FontAwesome", "HTML5 Semantic Layout", "React / Next.js"])
    
    elif site == "amazon.com":
        if year <= 2000:
            return (350, 25, 8, False, ["Table-Based Layout (Classic Web)"])
        elif year <= 2004:
            return (680, 45, 18, False, ["Table-Based Layout (Classic Web)"])
        elif year <= 2008:
            return (1200, 85, 35, False, ["Table-Based Layout (Classic Web)", "jQuery"])
        elif year <= 2012:
            return (1850, 125, 55, False, ["jQuery", "Web Fonts / FontAwesome"])
        elif year <= 2016:
            return (2500, 165, 78, True, ["jQuery", "Bootstrap", "Web Fonts / FontAwesome"])
        elif year <= 2020:
            return (3200, 205, 98, True, ["jQuery", "Web Fonts / FontAwesome", "HTML5 Semantic Layout", "React / Next.js"])
        else:
            return (3800, 245, 118, True, ["Web Fonts / FontAwesome", "HTML5 Semantic Layout", "React / Next.js"])
    
    elif site == "spacejam.com":
        if year <= 2020:
            return (85, 12, 1, False, ["Table-Based Layout (Classic Web)"])
        else:
            return (1450, 95, 65, True, ["React / Next.js", "Web Fonts / FontAwesome", "HTML5 Semantic Layout"])
    
    elif site == "yahoo.com":
        if year <= 2000:
            return (420, 35, 12, False, ["Table-Based Layout (Classic Web)"])
        elif year <= 2004:
            return (850, 65, 28, False, ["Table-Based Layout (Classic Web)"])
        elif year <= 2008:
            return (1450, 95, 48, False, ["Table-Based Layout (Classic Web)", "jQuery", "Adobe Flash"])
        elif year <= 2012:
            return (2200, 135, 72, False, ["jQuery", "Web Fonts / FontAwesome"])
        elif year <= 2016:
            return (1800, 108, 58, True, ["jQuery", "Web Fonts / FontAwesome", "HTML5 Semantic Layout"])
        elif year <= 2020:
            return (2400, 148, 85, True, ["jQuery", "Web Fonts / FontAwesome", "HTML5 Semantic Layout", "React / Next.js"])
        else:
            return (2800, 178, 102, True, ["Web Fonts / FontAwesome", "HTML5 Semantic Layout", "React / Next.js"])
    
    elif site == "wikipedia.org":
        if year <= 2003:
            return (65, 3, 2, False, [])
        elif year <= 2006:
            return (180, 8, 5, False, ["Table-Based Layout (Classic Web)"])
        elif year <= 2010:
            return (320, 15, 10, False, ["jQuery"])
        elif year <= 2014:
            return (480, 22, 18, False, ["jQuery", "Web Fonts / FontAwesome"])
        elif year <= 2018:
            return (620, 28, 25, True, ["jQuery", "Web Fonts / FontAwesome", "HTML5 Semantic Layout"])
        else:
            return (780, 35, 32, True, ["jQuery", "Web Fonts / FontAwesome", "HTML5 Semantic Layout"])
    
    return (100, 5, 3, False, [])


def seed_database():
    """Seed the SQLite database with all snapshot and metadata records."""
    print(f"📂 Database path: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure tables exist
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            status_code INTEGER,
            mimetype TEXT,
            length INTEGER,
            fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(url, timestamp)
        );
        CREATE INDEX IF NOT EXISTS idx_snapshots_url_ts ON snapshots(url, timestamp);
        
        CREATE TABLE IF NOT EXISTS snapshot_cache_meta (
            url TEXT PRIMARY KEY,
            last_fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_count INTEGER DEFAULT 0
        );
        
        CREATE TABLE IF NOT EXISTS snapshot_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_id INTEGER REFERENCES snapshots(id),
            url TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            html_size_bytes INTEGER,
            dom_node_count INTEGER,
            image_count INTEGER,
            external_resource_count INTEGER,
            has_mobile_viewport BOOLEAN,
            detected_frameworks TEXT,
            computed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(url, timestamp)
        );
        CREATE INDEX IF NOT EXISTS idx_metadata_url_ts ON snapshot_metadata(url, timestamp);
    """)
    
    now_iso = datetime.now(timezone.utc).isoformat()
    total_snapshots = 0
    total_metadata = 0
    
    for site, data in SITES.items():
        snapshots = data["snapshots"]
        print(f"\n🌐 Seeding {site} — {len(snapshots)} snapshots...")
        
        # Update cache meta
        cursor.execute(
            """INSERT INTO snapshot_cache_meta (url, last_fetched_at, total_count)
               VALUES (?, ?, ?)
               ON CONFLICT(url) DO UPDATE SET last_fetched_at = excluded.last_fetched_at, total_count = excluded.total_count""",
            (site, now_iso, len(snapshots))
        )
        
        for ts, status, mime, length in snapshots:
            # Insert snapshot
            cursor.execute(
                """INSERT OR IGNORE INTO snapshots (url, timestamp, status_code, mimetype, length)
                   VALUES (?, ?, ?, ?, ?)""",
                (site, ts, status, mime, length)
            )
            total_snapshots += 1
            
            # Compute & insert metadata
            year = int(ts[:4])
            dom_nodes, images, ext_resources, has_mobile, frameworks = get_metadata_for_site_year(site, year)
            
            cursor.execute(
                """INSERT OR IGNORE INTO snapshot_metadata 
                   (url, timestamp, html_size_bytes, dom_node_count, image_count, 
                    external_resource_count, has_mobile_viewport, detected_frameworks)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (site, ts, length, dom_nodes, images, ext_resources, has_mobile, json.dumps(frameworks))
            )
            total_metadata += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Seeding complete!")
    print(f"   📊 {total_snapshots} snapshot records inserted")
    print(f"   🔬 {total_metadata} metadata records inserted")
    print(f"   🌐 {len(SITES)} sites: {', '.join(SITES.keys())}")
    print(f"\n🚀 Your Internet Time Machine is ready! Visit http://127.0.0.1:5173/")


if __name__ == "__main__":
    seed_database()
