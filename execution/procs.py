import inspect, sys
bonus = {'heroic':1.15,
         'mythic':1.15*1.15}

class Proc(object):
  _gear = [999999]
  _magnitude = 0
  _duration = 0
  _cooldown = 0
  
  def gear(self):
    return isinstance(self._gear,int) and [self._gear] or self._gear
  
  def magnitude(self,gear):
    for g in gear:
      if g['id'] in self.gear():
        return g['bonus'] in bonus and bonus[ g['bonus'] ] * self._magnitude or self._magnitude
    return self._magnitude
  
  def equipped(self,gear):
    for g in gear:
      if g['id'] in self.gear():
        return True
    return False
  
  def uptime(self):
    return self.stat != 'dps' and self._duration / self._cooldown
  
  def total(self,gear,haste):
    if self.equipped(gear):
      return self.magnitude(gear) * self._duration / self._cooldown
    return 0
    
  def info(self,gear,haste):
    data = {'name': self.__doc__.strip(),
            'magnitude': self.magnitude(gear),
            'uptime': '%.02f' % (self.uptime()*100),
            'duration': self._duration,
            'equipped': self.equipped(gear),
            'effect': self.total(gear,haste),
            'effect_display': '%d %s' % (self.total(gear,haste),self.stat)}
    if hasattr(self,'_cooldown'):
      data['cooldown'] = self._cooldown
    if hasattr(self,'_rppm'):
      data['rppm'] = self._rppm
    return data
    
class OnUseProc(Proc):
  """ On Use Trinket """

class RPPMProc(Proc):
  """ RPPM Trinket """  
  
  def uptime(self):
    return self.stat != 'dps' and self._duration / (self._rppm*60)
 
  def total(self,gear,haste):
    if self.equipped(gear):
      use_haste = self.stat == 'dps' and haste or 1
      return self.magnitude(gear) * use_haste * self._duration / (self._rppm*60)
    return 0
  

class BHotM(OnUseProc):
  """ Beating Heart of the Mountain """
  stat = 'multistrike'
  _gear = 113931
  _magnitude = 1467
  _duration = 20
  _cooldown = 120
  
class BEM(RPPMProc):
  """ Blackheart Enforcer's Medallion """
  stat = 'multistrike'
  _gear = 116314
  _magnitude = 1665
  _duration = 10
  _rppm = 0.92
  
class HBT(RPPMProc):
  """ Humming Blackiron Trigger """
  stat = 'crit'
  _gear = 113985
  _magnitude = 131*10.5
  _duration = 10
  _rppm = 0.92

class MeatyDST(RPPMProc):
  """ Meaty Dragonspine Trophy """
  stat = 'haste'
  _gear = 118114
  _magnitude = 1913
  _duration = 10
  _rppm = 0.92

class ScalesOfDoom(RPPMProc):
  """ Scales of Doom """
  stat = 'multistrike'
  _gear = 113612
  _magnitude = 1743
  _duration = 10
  _rppm = 0.92
      
def proc_info(gear,haste):
  info = {}
  for stat in ('dps','agility','crit','haste','mastery','multistrike','versatility',):    
    klass = inspect.getmembers(sys.modules[__name__],lambda term: getattr(term,'stat','') == stat)
    on_use = [p() for name,p in inspect.getmembers(sys.modules[__name__],lambda term: getattr(term,'stat','') == stat) if isinstance(p,type) and issubclass(p,OnUseProc)]
    rppm = [p() for name,p in inspect.getmembers(sys.modules[__name__],lambda term: getattr(term,'stat','') == stat) if isinstance(p,type) and issubclass(p,RPPMProc)]
    
    proc_info = [proc.info(gear,haste) for proc in on_use+rppm if proc]
    totals = []
    for proc in proc_info:
      totals.append({'name':proc['name'],'effect':proc['effect']})
    info[stat] = {'summary':totals,
                  'total':sum([p['effect'] for p in proc_info]),
                  'info':proc_info}
  return info

res = proc_info([{'id':113931,'bonus':'normal'}],1.24)