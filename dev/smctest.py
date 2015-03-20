
from Data import log2oData as l
from Analysis import featureVector
from Analysis import analysis

data_path = "/home/kec/uploads/access.log110.76.72.14"
tab_path = "/home/kec/uploads/tab/access.log110.76.72.14.tab"
error_path = "/home/kec/uploads/error/access.log110.76.72.14.tab"
feature_path = "/home/kec/uploads/feature/access.log110.76.72.14.tab"

l.MyownOrange(data_path, tab_path, error_path)
featureVector.extract_feature(tab_path, feature_path)
result = analysis.getAnalysis(tab_path, feature_path, 4.0)

print result
