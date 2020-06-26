import os
import datetime
import pandas as pd
import pytz

class _Utilities(object):

    """
    /**
     * generates current date into fhir format 
     * @return date
     */
    """
    def getFhirDate(): 
        z = datetime.datetime.now(pytz.timezone('UTC')).strftime("%Y-%m-%dT%H:%M:%S%z")
        return z[:-2]+':'+z[-2:]

    def getSequenceRelation(phasedRecMap):
        RelationTable= pd.DataFrame(columns=['POS1','POS2','Relation'])
        for key in phasedRecMap:
            prev_record = None
            for record in phasedRecMap[key]:
                if prev_record is None:
                    prev_record = record
                    continue
                prev_data = prev_record.samples[0].data
                record_data = record.samples[0].data
                if(prev_data.PS == record_data.PS):
                    if prev_data.GT == record_data.GT:
                        RelationTable = RelationTable.append({'POS1': prev_record.POS, 'POS2': record.POS, 'Relation': 'Cis'}, ignore_index=True)
                    else:
                        RelationTable = RelationTable.append({'POS1': prev_record.POS, 'POS2': record.POS, 'Relation': 'Trans'}, ignore_index=True)
                prev_record = record
        return RelationTable

    def getAllelicState(record):
        allelicState = ''
        allelicCode = ''
        # Using  the first sample
        sample = record.samples[0]
        alleles = sample.gt_alleles
        if record.CHROM != 'M':
            if len(alleles) >= 2 and sample.gt_type == 1:
                allelicState = 'heterozygous'
                allelicCode = 'LA6706-1'
            elif len(alleles) >= 2:
                allelicState = 'homozygous'
                allelicCode = 'LA6705-3'
            elif sample.gt_type != None and len(alleles) == 1:
                allelicState = 'hemizygous'
                allelicCode = 'LA6707-9'
            else:
                allelicState = None
                allelicCode = None
        else:
            if sample.gt_type != None and len(alleles) == 1 and alleles[0] == '1':
                if hasattr(sample.data, 'AD') and hasattr(sample.data, 'DP'):
                    try:
                        ratio = sample.data.AD/sample.data.DP
                        if ratio > 0.99:
                            allelicState = "homoplasmic"
                            allelicCode = "LA6704-6"
                        else: 
                            allelicState = "heteroplasmic"
                            allelicCode = "LA6703-8"
                    except:
                        pass
                else:
                    allelicState = ""
                    allelicCode = ""
        return {'ALLELE': allelicState, 'CODE' : allelicCode}
        