class Model(object):
    def __init__(self,**kwargs):
        keys = dir(self)
        self.defaults()
        self.attr = []
        for k in dir(self):
            if k not in keys:
                self.attr.append(k)
        self.__dict__.update(kwargs)
        
class Location(Model):
    def defaults(self):
        self.name = "Seattle"
        self.people = []
    def turn(self,context):
        context["location"] = self
        for p in self.people:
            p.turn(context)
    def add(self,p):
        self.people.append(p)
    def remove(self,p):
        print "removing",p.name
        if p in self.people:
            self.people.remove(p)

class Population(Model):
    def defaults(self):
        self.name = "fred"
        self.size = 1000 #how many people I represent
        self.lifestyle = 0  #healthy lifestyle? poor? smokers? etc
        self.race = "white"  #what race they are
        self.age = 18   #average age
        self.mobility = 2  #how many turns between travelling
        self.trust = 0  #How likely they are to trust the media
        
        self.travel_history = []  #first entry is their home
        self.illnesses = []
        self.immunities = set()
    def symptoms(self):
        symptoms = set()
        for i in self.illnesses:
            for s in i.symptoms():
                symptoms.add(s)
        return symptoms
    def turn(self,context):
        context["population"] = self
        for s in self.symptoms():
            if s.name == "death":
                context["location"].remove(self)
                n = context.get("dead",0)
                n+=1
                context["dead"] = n
        for i in self.illnesses:
            i.turn(context)
    def remove_disease(self,d):
        if d in self.illnesses:
            self.illnesses.remove(d)
        
class Symptom(Model):
    def defaults(self):
        self.name = "cough"
        self.visibility = 1  #How likely to detect/how likely they are in the hospital
        self.lethality = 0  #How likely for symptom to kill someone
        self.spread = 2   #Modifies spread
        self.spread_types = ["air"]   #Spread modifier only if type matches
    def __repr__(self):
        return self.name
        
class Stage(Model):
    def defaults(self):
        self.length = 2   #Number of turns for this stage
        self.spread = 1  #Power of contagion to spread to another host
        self.weakness = 1  #Weakness to drugs
        self.symptoms = []   #What symptoms appear
    def mspread(self,types):
        """Return spread modified by symptoms"""
        sp = self.spread
        if not sp:
            return 0
        for s in self.symptoms:
            for st in s.spread_types:
                if st in types:
                    sp+=s.spread
                    break
        return sp
        
class Disease(Model):
    def defaults(self):
        self.stages = []
        self.spread_methods = ["touch"]       #How disease is spread
        
        self.age = 0                                     #Current life
        self.mutations = 0                              #How many mutations we have gone through
        
        self.add_stage_chance = 0               #In mutation how likely to add a stage
        self.remove_stage_chance = 0            #In mutation how likely to remove a stage
        
        self.alter_stage_chance = 1                 #how likely to change a stage
        self.add_symptom_chance = 1               #Add a symptom to a changing stage
        self.remove_symptom_chance = 1          #Remove a symptom from a changing stage
        self.change_symptom_chance = 1          #Change a symptom
        
        self.add_spread_method_chance = 1       #How likely to add a new spread method
        self.alter_spread_method_chance = 2     #How likely to change a spread method to something else
        self.name = "H1N16"                         #Name given to disease once discovered, used as seed for random?
    def get_stage(self):
        """Gets the stage we are currently on"""
        c = 0
        for s in self.stages:
            c += s.length
            if c>self.age:
                return s
        #All stages complete, we are no longer infected!
        return None
    def symptoms(self):
        s = self.get_stage()
        if not s:
            return []
        return s.symptoms
    def turn(self,context):
        context["disease"] = self
        print "turn",id(self)
        self.spread(context["location"])
        self.age += 1
        if not self.get_stage():
            context["population"].remove_disease(self)
    def spread(self,location):
        s = self.get_stage()
        if not s:
            return
        people = [p for p in location.people if self.name not in p.immunities]
        best = None
        bscore = 0
        m = s.mspread(self.spread_methods)
        if not m:
            return
        for p in people:
            score = m-p.lifestyle
            if score>bscore:
                best = p
                bscore = score
        if best:
            infect(self,best)
    def copy(self):
        """Copy disease so it can be used on a new population"""
        a = {}
        for k in self.attr:
            if k in ["age","mutations"]:
                continue
            a[k] = self.__dict__[k]
        return Disease(**a)

def inhabit(location,population):
    location.people.append(population)
def infect(disease,population):
    """After building a disease, inflict it on a population."""
    population.illnesses.append(disease.copy())
    population.immunities.add(disease.name)
    
cough = Symptom(name="cough",visibiliy=1,lethality=1,spread=2,spread_types=['air'])
diarrhea = Symptom(name="diarrhea",visibility=1,lethality=1,spread=1,spread_types=['touch'])
stomach_pain = Symptom(name="stomach pain",visibility=2,lethality=1,spread=0)
headache = Symptom(name="headache",visibility=2,lethality=0,spread=0)
death = Symptom(name="death",visibility=10,lethality=10,spread=2,spread_types=['touch','air'])
        
x = Disease(
                stages=[
                    Stage(length=1,spread=0,weakness=2,symptoms=[cough]),
                    Stage(length=2,spread=1,weakness=1,symptoms=[cough,diarrhea,stomach_pain]),
                    Stage(length=1,spread=2,weakness=1,symptoms=[death])
                    ],
                spread_methods=["air"],
                name="H1N8M7G9"
                )
bob = Population(name="Bob")
infect(x,bob)
anna = Population(name="Anna")
infect(x,anna)
jane = Population(name="Jane")
seattle = Location()
inhabit(seattle,anna)
inhabit(seattle,bob)
inhabit(seattle,jane)
for i in range(10):
    inhabit(seattle,Population(name="dummy%s"%i))
t = 0
dead = 0
while seattle.people:
    print t
    t += 1
    for p in seattle.people:
        print p.name,p.symptoms()
    print "# infected:",len([x for x in seattle.people if x.illnesses])
    d = {}
    seattle.turn(d)
    dead += d.get("dead",0)
    print "# dead:",dead