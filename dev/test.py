from Data import log2oData as l
from Analysis import featureVector
from Analysis import analysis

datapath = "/home/kec/uploads/access.log.2110.76.72.14"
tab_path = "/home/kec/uploads/tab/access.log.2110.76.72.14.tab"
error_path = "/home/kec/uploads/error/access.log.2110.76.72.14.tab"
feature_path = "/home/kec/uploads/feature/access.log.2110.76.72.14.tab"
save_path = "save.tab"

l.MyownOrange(datapath, tab_path, error_path)
featureVector.extract_feature(tab_path, feature_path)
result = analysis.getAnalysis(feature_path, 4.0, save_path)

print result
