
import unittest

class cfgTests(unittest.TestCase): 
    def redundanceTest(self, cfg):
        stack = [cfg.get_root()]
        cfg.clear_visit()
        while len(stack) > 0:
            curr = stack.pop()
            if curr.is_visited():
                continue
            curr.visit()
            srcs = curr.get_parents()
            dsts = curr.get_children()
            self.assertFalse(not curr.has_insts() and curr.get_type == 'normal' and len(srcs) <= 1 and len(dsts) <= 1)
        for dst_name, dst in dsts.items():
            stack.append(dst)
