import conceptdb
from conceptdb.metadata import Dataset
from conceptdb.assertion import Assertion
from conceptdb.justify import Reason
from mongoengine.queryset import QuerySet

'''
Given two dbs, merges them
Merge should:
- Add assertions to both DBs that are new
- NOT add multiple assertions (defined as: same dataset, relation, concepts, polarity, weight) -- Assertion IDs will still change
- Add reasons pointing to new assertions
- Add reasons pointing to old assertions, changing the reason's target to the new DB's Assertion ID for the matching assertion
'''
def merge(db1, db2):
    ''' 
    Loop over both of the DBs to find assertions that are not present in each, and 
    reasons that point to those assertions
    '''
    db1_tobeadded = []
    db2_tobeadded = []
    
    conceptdb.connect_to_mongodb(db1)
    db1_assertions = Assertion.objects
    
    conceptdb.connect_to_mongodb(db2)
    db2_assertions = Assertion.objects
    # Looping to find assertions in DB1 that are not in DB2
    for db1_a in [a1 for a1 in list(db1_assertions) if a1 not in list(db2_assertions)]:
        conceptdb.connect_to_mongodb(db1)
        # New assertions, along with the reasons
        db2_tobeadded.append((db1_a, Reason.objects.filter(target=db1_a.name)))
        # Check that each assertion does not exist in the DB with a different Assertion ID
        for db2_check in list(db2_assertions):
            if assertion_check(db1_a, db2_check):
                # Do not add multiple assertions
                db2_tobeadded.pop()
                # But DO add new reasons that point to existing assertions
                if Reason.objects.filter(target=db1_a.name) is not None:
                    db2_tobeadded.append((None, (Reason.objects.filter(target=db1_a.name), db2_check)))
                break         
    # Looping to find assertions in DB2 that are not in DB1
    for db2_a in [a2 for a2 in list(db2_assertions) if a2 not in list(db1_assertions)]:
        conceptdb.connect_to_mongodb(db2)
        # New assertions, along with the reasons
        db1_tobeadded.append((db2_a, Reason.objects.filter(target=db2_a.name)))
        # Check that each assertion does not exist in the DB with a different Assertion ID
        for db1_check in list(db1_assertions):
            if assertion_check(db2_a, db1_check):
                # Do not add multiple assertions
                db1_tobeadded.pop()
                # But DO add new reasons that point to existing assertions
                if Reason.objects.filter(target=db2_a.name) is not None:
                    db1_tobeadded.append((None, (Reason.objects.filter(target=db2_a.name), db1_check)))
                break
   
    '''
    Step through db1_tobeadded and db2_tobeadded, lists of elements that have to be added
    from each DB to the other, and add all of the assertions and corresponding reasons to the 
    DBs
    '''
    # Adding to DB1
    conceptdb.connect_to_mongodb(db1)       
    for (add1,rel1) in db1_tobeadded:
        if add1 == None:
            for r1 in list(rel1[0]):
                if Reason.objects.filter(target=rel1[1],factors=r1.factors,weight=r1.weight, polarity=r1.polarity) ==None:
#                    Reason.make(target=rel1[1],
#                                factors=r1.factors,
#                                weight=r1.weight,
#                                polarity=r1.polarity
#                                )
                    rel1[1].add_support(r1.factors, r1.weight)
            continue
        ass1 = db1_assertions.create(
                              dataset=add1.dataset,
                              relation=add1.relation,
                              polarity=add1.polarity,
                              argstr=add1.argstr,
                              context=add1.context,
                              complete=1
                              )
        for r1 in list(rel1):
#            Reason.make(target=ass1.name,
#                        factors=r1.factors,
#                        weight=r1.weight,
#                        polarity=r1.polarity
#                        )
            ass1.add_support(r1.factors, r1.weight)
    # Adding to DB2
    conceptdb.connect_to_mongodb(db2)
    for (add2,rel2) in db2_tobeadded:
        if add2 == None:
            for r2 in list(rel2[0]):
                if Reason.objects.filter(target=rel2[1],factors=r2.factors,weight=r2.weight, polarity=r2.polarity) ==None:
#                    Reason.make(target=rel2[1],
#                                factors=r2.factors,
#                                weight=r2.weight,
#                                polarity=r2.polarity
#                                )
                    rel2[1].add_support(r2.factors, r2.weight)
            continue
        ass2 = db2_assertions.create(
                              dataset=add2.dataset,
                              relation=add2.relation,
                              polarity=add2.polarity,
                              argstr=add2.argstr,
                              context=add2.context,
                              complete=1
                              )
        for r2 in list(rel2):
#            Reason.make(target=ass2.name,
#                        factors=r2.factors,
#                        weight=r2.weight,
#                        polarity=r2.polarity
#                        )
            ass2.add_support(r2.factors, r2.weight)
        
    
    return (db1_assertions, db2_assertions)

def merge_dset(db1, db2, dset):
    ''' 
    Loop over both of the DBs to find assertions that are not present in each, and 
    reasons that point to those assertions
    '''
    db1_tobeadded = []
    db2_tobeadded = []
    
    conceptdb.connect_to_mongodb(db1)
    db1_assertions = Assertion.objects.filter(dataset=dset)
    
    conceptdb.connect_to_mongodb(db2)
    db2_assertions = Assertion.objects.filter(dataset=dset)
    # Looping to find assertions in DB1 that are not in DB2
    for db1_a in [a1 for a1 in list(db1_assertions) if a1 not in list(db2_assertions)]:
        conceptdb.connect_to_mongodb(db1)
        # New assertions, along with the reasons
        db2_tobeadded.append((db1_a, Reason.objects.filter(target=db1_a.name)))
        # Check that each assertion does not exist in the DB with a different Assertion ID
        for db2_check in list(db2_assertions):
            if assertion_check(db1_a, db2_check):
                # Do not add multiple assertions
                db2_tobeadded.pop()
                # But DO add new reasons that point to existing assertions
                if Reason.objects.filter(target=db1_a.name) is not None:
                    db2_tobeadded.append((None, (Reason.objects.filter(target=db1_a.name), db2_check)))
                break         
    # Looping to find assertions in DB2 that are not in DB1
    for db2_a in [a2 for a2 in list(db2_assertions) if a2 not in list(db1_assertions)]:
        conceptdb.connect_to_mongodb(db2)
        # New assertions, along with the reasons
        db1_tobeadded.append((db2_a, Reason.objects.filter(target=db2_a.name)))
        # Check that each assertion does not exist in the DB with a different Assertion ID
        for db1_check in list(db1_assertions):
            if assertion_check(db2_a, db1_check):
                # Do not add multiple assertions
                db1_tobeadded.pop()
                # But DO add new reasons that point to existing assertions
                if Reason.objects.filter(target=db2_a.name) is not None:
                    db1_tobeadded.append((None, (Reason.objects.filter(target=db2_a.name), db1_check)))
                break
   
    '''
    Step through db1_tobeadded and db2_tobeadded, lists of elements that have to be added
    from each DB to the other, and add all of the assertions and corresponding reasons to the 
    DBs
    '''
    # Adding to DB1
    conceptdb.connect_to_mongodb(db1)       
    for (add1,rel1) in db1_tobeadded:
        if add1 == None:
            for r1 in list(rel1[0]):
                if Reason.objects.filter(target=rel1[1],factors=r1.factors,weight=r1.weight, polarity=r1.polarity) ==None:
#                    Reason.make(target=rel1[1],
#                                factors=r1.factors,
#                                weight=r1.weight,
#                                polarity=r1.polarity
#                                )
                    rel1[1].add_support(r1.factors, r1.weight)
            continue
        ass1 = db1_assertions.create(
                              dataset=add1.dataset,
                              relation=add1.relation,
                              polarity=add1.polarity,
                              argstr=add1.argstr,
                              context=add1.context,
                              complete=1
                              )
        for r1 in list(rel1):
#            Reason.make(target=ass1.name,
#                        factors=r1.factors,
#                        weight=r1.weight,
#                        polarity=r1.polarity
#                        )
            ass1.add_support(r1.factors, r1.weight)
    # Adding to DB2
    conceptdb.connect_to_mongodb(db2)
    for (add2,rel2) in db2_tobeadded:
        if add2 == None:
            for r2 in list(rel2[0]):
                if Reason.objects.filter(target=rel2[1],factors=r2.factors,weight=r2.weight, polarity=r2.polarity) ==None:
#                    Reason.make(target=rel2[1],
#                                factors=r2.factors,
#                                weight=r2.weight,
#                                polarity=r2.polarity
#                                )
                    rel2[1].add_support(r2.factors, r2.weight)
            continue
        ass2 = db2_assertions.create(
                              dataset=add2.dataset,
                              relation=add2.relation,
                              polarity=add2.polarity,
                              argstr=add2.argstr,
                              context=add2.context,
                              complete=1
                              )
        for r2 in list(rel2):
#            Reason.make(target=ass2.name,
#                        factors=r2.factors,
#                        weight=r2.weight,
#                        polarity=r2.polarity
#                        )
            ass2.add_support(r2.factors, r2.weight)
        
    
    return (db1_assertions, db2_assertions)
    
        
'''
Two assertion have the same dataset, arguments, relation, polarity, and context
'''                                       
def assertion_check(ass1, ass2):
    if ass1.dataset==ass2.dataset and ass1.argstr==ass2.argstr and ass1.relation==ass2.relation and ass1.polarity==ass2.polarity and ass1.context==ass2.context:
        return True
    return False

'''
Creates two test dbs, calls merge
'''
def test_merge1(db1, db2):
    '''
    Load test assertions into the two DBs:
    DB1: Assertions 0-9
    DB2: Assertions 0-4
    '''
    conceptdb.create_mongodb(db1)
    Assertion.drop_collection()
    Dataset.drop_collection()  
    Reason.drop_collection()
    for i in xrange(10):
        a = Assertion.make('/data/test','/rel/IsA',['/test/assertion','test/test%d'%i])
        a.add_support(['/data/test/contributor/nholm'])     
    print "Before the merge, db %s has the following assertions: "%db1
    for a1 in Assertion.objects:
        print "assertion: %s"%a1
        print "     confidence score: %s"%a1.confidence
        for r1 in list(Reason.objects.filter(target=a1.name)):
            print "     reason: %s"%r1.factors
            assert r1.target == a1.name

    
    conceptdb.create_mongodb(db2)
    Assertion.drop_collection()
    Dataset.drop_collection()
    Reason.drop_collection()
    for i in xrange(5):
        a1 = Assertion.make('/data/test','/rel/IsA',['/test/assertion','test/test%d'%i])  
        a1.add_support(['/data/test/contributor/nholm'])
        a2 = Assertion.make('/data/test','/rel/HasA',['/test/assertion','test/test%d'%i])  
        a2.add_support(['/data/test/contributor/nholm'])  
        a2.add_support(['/data/test/contributor/nholm1'])
        a2.add_support(['/data/test/contributor/nholm2'])
        a2.add_support(['/data/test/contributor/nholm3'])
        a2.add_support(['/data/test/contributor/nholm4']) 
    print "Before the merge, db %s has the following assertions: "%db2
    for a2 in Assertion.objects:
        print "assertion: %s"%a2
        print "     confidence score: %s"%a2.confidence
        for r2 in list(Reason.objects.filter(target=a2.name)):
            print "     reason: %s"%r2.factors
            assert r2.target == a2.name

    
    '''
    Merge the two dbs
    '''
    merge(db1, db2)
    
    '''
    Check post-merge elements, make sure they match
    '''
    conceptdb.connect_to_mongodb(db1)
    print "After the merge, db %s has the following assertions: "%db1
    for a4 in Assertion.objects:
        print "assertion: %s"%a4 
        print "     confidence score: %s"%a4.confidence
        for r4 in list(Reason.objects.filter(target=a4.name)):
            print "     reason: %s"%r4.factors
            assert r4.target == a4.name


    Assertion.drop_collection()
    Dataset.drop_collection()
    Reason.drop_collection()
    
    conceptdb.connect_to_mongodb(db2)
    print "After the merge, db %s has the following assertions: "%db2
    for a3 in Assertion.objects:
        print "assertion: %s"%a3
        print "     confidence score: %s"%a3.confidence
        for r3 in list(Reason.objects.filter(target=a3.name)):
            print "     reason: %s"%r3.factors
            assert r3.target == a3.name

    Assertion.drop_collection() 
    Dataset.drop_collection()
    Reason.drop_collection()
    
    
def test_merge2(db1, db2):
    '''
    Load test assertions into the two DBs:
    DB1: Assertions 0-9
    DB2: Assertions 0-4
    '''
    conceptdb.create_mongodb(db1)
    Assertion.drop_collection()
    Dataset.drop_collection()  
    Reason.drop_collection()
    for i in xrange(10):
        a = Assertion.make('/data/test','/rel/IsA',['/test/assertion','test/test%d'%i])
        a.add_support(['/data/test/contributor/nholm'])    
        a0 = Assertion.make('/data/test1','/rel/IsA',['/test/assertion','test/test%d'%i]) 
        a0.add_support(['/data/test1/contributor/nholm'])    
    print "Before the merge, db %s has the following assertions: "%db1
    for a1 in Assertion.objects:
        print "assertion: %s"%a1
        print "     confidence score: %s"%a1.confidence
        for r1 in list(Reason.objects.filter(target=a1.name)):
            print "     reason: %s"%r1.factors
            assert r1.target == a1.name

    
    conceptdb.create_mongodb(db2)
    Assertion.drop_collection()
    Dataset.drop_collection()
    Reason.drop_collection()
    for i in xrange(5):
        a1 = Assertion.make('/data/test','/rel/IsA',['/test/assertion','test/test%d'%i])  
        a1.add_support(['/data/test/contributor/nholm'])
        a2 = Assertion.make('/data/test','/rel/HasA',['/test/assertion','test/test%d'%i])  
        a2.add_support(['/data/test/contributor/nholm'])  
        a3 = Assertion.make('/data/test1','/rel/CausesDesire',['/test/assertion','test/test%d'%i])  
        a3.add_support(['/data/test1/contributor/nholm'])
        
    print "Before the merge, db %s has the following assertions: "%db2
    for a2 in Assertion.objects:
        print "assertion: %s"%a2
        print "     confidence score: %s"%a2.confidence
        for r2 in list(Reason.objects.filter(target=a2.name)):
            print "     reason: %s"%r2.factors
            assert r2.target == a2.name

    
    '''
    Merge the two dbs
    '''
    merge_dset(db1, db2, '/data/test')
    
    '''
    Check post-merge elements, make sure they match
    '''
    conceptdb.connect_to_mongodb(db1)
    print "After the merge, db %s has the following assertions: "%db1
    for a4 in Assertion.objects:
        print "assertion: %s"%a4 
        print "     confidence score: %s"%a4.confidence
        for r4 in list(Reason.objects.filter(target=a4.name)):
            print "     reason: %s"%r4.factors
            assert r4.target == a4.name


    Assertion.drop_collection()
    Dataset.drop_collection()
    Reason.drop_collection()
    
    conceptdb.connect_to_mongodb(db2)
    print "After the merge, db %s has the following assertions: "%db2
    for a3 in Assertion.objects:
        print "assertion: %s"%a3
        print "     confidence score: %s"%a3.confidence
        for r3 in list(Reason.objects.filter(target=a3.name)):
            print "     reason: %s"%r3.factors
            assert r3.target == a3.name

    Assertion.drop_collection() 
    Dataset.drop_collection()
    Reason.drop_collection()
    
    