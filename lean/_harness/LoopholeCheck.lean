import Opt8
open PHTax

#eval ("income_gt_gross_checkT", checkT (mkCertT 100000000 10000000000 30), (mkCertT 100000000 10000000000 30).total)
#eval ("income_gt_gross_check8", check8 (mkCert8 100000000 10000000000 30 false), (mkCert8 100000000 10000000000 30 false).total)
#eval ("retro_graduated", check8 (mkCert8 300000000 300000000 30 false), (mkCert8 300000000 300000000 30 false).total)
#eval ("retro_eight", check8 (mkCert8 300000000 300000000 30 true), (mkCert8 300000000 300000000 30 true).total)
#eval ("cliff_below_20M", check8 (mkCert8 1999999999 1500000000 30 false), (mkCert8 1999999999 1500000000 30 false).total)
#eval ("cliff_at_20M", check8 (mkCert8 2000000000 1500000000 30 false), (mkCert8 2000000000 1500000000 30 false).total)
#eval ("trap_graduated", check8 (mkCert8 300000000 25000000 30 false), (mkCert8 300000000 25000000 30 false).total)
#eval ("trap_eight", check8 (mkCert8 300000000 25000000 30 true), (mkCert8 300000000 25000000 30 true).total)
#eval ("crossover_at", check8 (mkCert8 300000000 91000000 30 true), (mkCert8 300000000 91000000 30 true).total)
#eval ("crossover_below", check8 (mkCert8 300000000 90999999 30 true), (mkCert8 300000000 90999999 30 true).total)
#eval ("hundred_years_late", check8 (mkCert8 150000000000 5000000000 36500 false), (mkCert8 150000000000 5000000000 36500 false).total)
