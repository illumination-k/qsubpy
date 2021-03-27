from qsubpy import qsub

def test_get_jid():
    with open("test/sge_out.txt") as f:
        out = f.read()
    exspected = "33733899"
    jid = qsub.get_jid(out)
    assert jid == exspected, f'expected jid is {exspected}, but get {jid}'

def test_get_jid_array():
    with open("test/sge_out_array.txt") as f:
        out = f.read()
    
    exspected = "33734360"
    jid = qsub.get_jid(out)
    assert jid == exspected, f'expected jid is {exspected}, but get {jid}'