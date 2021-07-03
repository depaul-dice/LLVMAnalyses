
import unittest

class cfgTests(unittest.TestCase): 
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg

    def nodeCorrespondenceTest(self):
        numNodes = len(self.cfg.get_vertices())
        print(self.cfg.name)
        stack = [self.cfg.get_root()]
        self.cfg.clear_visit()
        cnt = 0 
        
        while len(stack) > 0:
            curr = stack.pop()
            if curr.is_visited():
                continue
            cnt += 1
            curr.visit()
            dsts = curr.get_children() 
            print(dsts)
            for dName, dst in dsts.items():
                stack.append(dst)
        self.cfg.clear_visit()
        self.assertEqual(cnt, numNodes)

    def edgeCorrespondenceTest(self):
        stack = [self.cfg.get_root()] 
        self.cfg.clear_visit()
        iEdges = dict() # key, value = src, dst
        oEdges = dict() # key, value = src, dst
        while len(stack) > 0:
            curr = stack.pop()
            if curr.is_visited():
                continue
            curr.visit()
            srcs = curr.get_parents()
            for sName, src in srcs.items():
                iEdges[sName] = curr.get_name()

            dsts = curr.get_children()
            for dName, dst in dsts.items():
                oEdges[curr.get_name()] = dName

        for dst_name, dst in dsts.items():
            stack.append(dst)
        self.cfg.clear_visit()

        for sName, dName in iEdges.items():
            self.assertTrue(sName in oEdges)
            self.assertEqual(dName, oEdges[sName])

    def redundanceTest(self):
        stack = [self.cfg.get_root()]
        self.cfg.clear_visit()
        while len(stack) > 0:
            curr = stack.pop()
            if curr.is_visited():
                continue
            curr.visit()
            srcs = curr.get_parents()
            dsts = curr.get_children()
            self.assertFalse((not curr.has_insts()) and curr.get_type == 'normal' and len(srcs) <= 1 and len(dsts) <= 1)
        for dst_name, dst in dsts.items():
            stack.append(dst)
        self.cfg.clear_visit()


