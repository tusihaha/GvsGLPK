class Graph(object):
    """
    Description: Course timetabling by graph coloring.
    """
    def __init__(self, e1, e2):
        """
        Args: Edges of possibility graph.
        Example: e1 = [('A', 'a'), ('B', 'b')]
                 e2 = [('1', 'a'), ('2', 'b')]
        """
        self.v1 = dict()
        self.v2 = dict()
        self.v3 = dict()
        self.asg = [dict(), dict()]

        for (t, c) in e1:
            if t not in self.v1:
                self.v1[t] = [0, [c]]
            else:
                self.v1[t][1].append(c)
            if c not in self.v2:
                self.v2[c] = [False, [t], []]
            else:
                self.v2[c][1].append(t)
        for (r, c) in e2:
            if r not in self.v3:
                self.v3[r] = [0, [c]]
            else:
                self.v3[r][1].append(c)
            self.v2[c][2].append(r)

    def select(self, part):
        """
        Description: Select teacher and room for courses
        Args: 0 - teachers and courses
              1 - room and courses
        """
        degree = 0
        for c in self.v2:
            p = self.findpath(c, degree, part)
            if p == False:
                v = self.v2[c][1 + part][0]
                if part == 0:
                    self.v1[v][0] += 1
                else:
                    self.v3[v][0] += 1
                self.asg[part][c] = v
                degree += 1
                self.v2[c][0] = v
            else:
                self.move(p, part)
        for c in self.v2:
            self.v2[c][0] = False

    def findpath(self, course, degree, part):
        if part == 0:
            resource = self.v1
        else:
            resource = self.v3
        red = list()
        green = list()
        orange = [course]
        for v in resource:
            if resource[v][0] == degree:
                red.append(v)
            else:
                green.append(v)
        for c in self.v2:
            v = self.v2[c][0]
            if v != False and v in red:
                orange.append(c)
        l = list()
        turn = 0
        group = green.copy()
        while group:
            nextgroup = list()
            d = dict()
            for v in group:
                if turn == 0:
                    for c in resource[v][1]:
                        if c not in d and c in orange:
                            d[c] = v
                            nextgroup.append(c)
                            orange.remove(c)
                        if c == course:
                            l.append(d)
                            path = [c]
                            for layer in l[::-1]:
                                path.append(layer[path[-1]])
                            return path
                else:
                    rs = self.v2[v][0]
                    if rs != False and rs in red:
                        d[rs] = v
                        nextgroup.append(rs)
                        red.remove(rs)
            turn = (turn + 1) % 2
            group = nextgroup.copy()
            l.append(d)
        return False

    def move(self, p, part):
        for i in range(0, len(p), 2):
            self.asg[part][p[i]] = p[i + 1]
            self.v2[p[i]][0] = p[i + 1]
        if part == 0:
            self.v1[p[-1]][0] += 1
        else:
            self.v3[p[-1]][0] += 1

    def make_regular(self):
        bgraph_v1 = dict()
        bgraph_v2 = dict()
        bgraph_e = dict()
        degree = 0
        for e in self.asg[0]:
            if self.asg[0][e] not in bgraph_v1:
                bgraph_v1[self.asg[0][e]] = [True, [e]]
            else:
                bgraph_v1[self.asg[0][e]][1].append(e)
            if len(bgraph_v1[self.asg[0][e]][1]) > degree:
                degree = len(bgraph_v1[self.asg[0][e]][1])
            bgraph_e[e] = [True, [self.asg[0][e]]]
        for e in self.asg[1]:
            if self.asg[1][e] not in bgraph_v2:
                bgraph_v2[self.asg[1][e]] = [True, [e]]
            else:
                bgraph_v2[self.asg[1][e]][1].append(e)
            if len(bgraph_v2[self.asg[1][e]][1]) > degree:
                degree = len(bgraph_v2[self.asg[1][e]][1])
            bgraph_e[e][1].append(self.asg[1][e])
        add_v = len(bgraph_v1) - len(bgraph_v2)
        if add_v < 0:
            for i in range(-add_v):
                bgraph_v1[i] = [False, []]
        else:
            for i in range(add_v):
                bgraph_v2[i] = [False, []]

        e_count = 0
        for v1 in bgraph_v1:
            while len(bgraph_v1[v1][1]) < degree:
                bgraph_v1[v1][1].append(e_count)
                for v2 in bgraph_v2:
                    if len(bgraph_v2[v2][1]) < degree:
                        bgraph_v2[v2][1].append(e_count)
                        bgraph_e[e_count] = [False, [v1, v2]]
                        break
                e_count += 1
        self.bgraph_v1 = bgraph_v1.copy()
        self.bgraph_v2 = bgraph_v2.copy()
        self.bgraph_e = bgraph_e.copy()
        self.degree = degree

    def edges_color(self):
        self.matching = list()
        while self.degree > 0:
            for e in self.bgraph_e:
                self.bgraph_e[e].append(1)
            while True:
                c = self.findckt()
                if c == False:
                    break
                else:
                    sum_m = 0
                    sum_n = 0
                    for i in range(len(c)):
                        if i % 2 == 0:
                            sum_m += self.bgraph_e[c[i]][2]
                        else:
                            sum_n += self.bgraph_e[c[i]][2]
                    if sum_m < sum_n:
                        for i in range(len(c)):
                            if i % 2 == 0:
                                self.bgraph_e[c[i]][2] -= 1
                            else:
                                self.bgraph_e[c[i]][2] += 1
                    else:
                        for i in range(len(c)):
                            if i % 2 == 1:
                                self.bgraph_e[c[i]][2] -= 1
                            else:
                                self.bgraph_e[c[i]][2] += 1
            colored_e = dict()
            for e in self.bgraph_e:
                if self.bgraph_e[e][2] > 0:
                    colored_e[e] = self.bgraph_e[e][:2]
                else:
                    self.bgraph_e[e] = self.bgraph_e[e][:2]
            for e in colored_e:
                    self.bgraph_e.pop(e)
            for v1 in self.bgraph_v1:
                for e in self.bgraph_v1[v1][1]:
                    if e in colored_e:
                        self.bgraph_v1[v1][1].remove(e)
            for v2 in self.bgraph_v2:
                for e in self.bgraph_v2[v2][1]:
                    if e in colored_e:
                        self.bgraph_v2[v2][1].remove(e)
            self.matching.append(colored_e)
            self.degree -= 1

    def findckt(self):
        circuit = False
        for e in self.bgraph_e:
            if 0 < self.bgraph_e[e][2] and self.bgraph_e[e][2] < self.degree:
                circuit = True
                break
        if circuit == True:
            for v1 in self.bgraph_v1:
                for e in self.bgraph_v1[v1][1]:
                    if 0 < self.bgraph_e[e][2] and self.bgraph_e[e][2] < self.degree:
                        v = self.bgraph_e[e][1][::-1]
                        c = [e]
                        turn = 0
                        break
            while True:
                if turn == 1:
                    for e in self.bgraph_v2[v[-1]][1]:
                        if e not in c and 0 < self.bgraph_e[e][2] and self.bgraph_e[e][2] < self.degree:
                            endpath = self.bgraph_e[e][1][0]
                            c.append(e)
                            if endpath in v:
                                p = c[v.index(endpath):]
                                return p
                            else:
                                v.append(endpath)
                                break
                    turn = 0
                else:
                    for e in self.bgraph_v1[v[-1]][1]:
                        if e not in c and 0 < self.bgraph_e[e][2] and self.bgraph_e[e][2] < self.degree:
                            endpath = self.bgraph_e[e][1][1]
                            c.append(e)
                            if endpath in v:
                                p = c[v.index(endpath):]
                                return p
                            else:
                                v.append(endpath)
                                break
                    turn = 1
            else:
                pass
        return False

    def info(self, filename):
        f = open(filename, 'w')
        f.write('Timeslot use: ' + str(len(self.matching)) + '\n\n')
        timeslot_count = 1
        for d in self.matching:
            f.write("Timeslot " + str(timeslot_count) + ':\n')
            for i in d:
                if d[i][0] == True:
                    f.write(str(i) + ' ' + str(d[i][1][0]) + ' ' + str(d[i][1][1]) + '\n')
            f.write('\n')
            timeslot_count += 1
        f.close()