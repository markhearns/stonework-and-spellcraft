"""Chapter two's authored plans. Mechanics are fixed and shown before commitment."""
PATHS = {
 'scholarship': {
  'title':'A working archive','room':'library','site':'quarry-shelter','approach':'survey','research':'archive-foundations',
  'cost':16,'inputs':{'porous-clay':1,'binding-thread':2},'work':6,'advisers':['mira','tamsin','elowen','koharu'],
  'proposal':'The collection is usable, but every question still begins with a search through unrelated papers. A proper working archive could give unfinished questions a place of their own.',
  'voice':'“A library should help you find the next question, not merely protect the last answer. Shall we make this one useful?”',
  'field':'The quarry shelter’s shutter notes offer a way to protect working papers without shutting out the room. Bring the survey home before drawing up the archive fittings.',
  'complication':'The first shelf plan is admirably efficient. It also takes the space beside the window where someone might sit with a notebook. There is room for precise indexing or a generous shared copying table, but not both in this installation.',
  'designs':{
   'index':{'name':'Indexed reference wall','description':'Narrow labelled drawers, cord-bound folders and a standing reference ledge keep working notes within reach. The window corner remains small.','benefit':'+1 work per assigned shared researcher. Ordinary personal study and spell work keep their own rates.','effect':'research','amount':1,'response':'You keep the reference wall compact and precise. There is space for a single notebook beneath each run of drawers; the larger communal table must wait.'},
   'table':{'name':'Shared copying table','description':'A long, clear table takes the window light, with two pull-out rests and open shelves for current work. The detailed index remains modest.','benefit':'+2 crowns per assigned founder copying phase. No unattended income.','effect':'copy','amount':2,'response':'You shorten the shelving run and give the window to the table. Finding an obscure note may still take patience, but ordinary work will have room to breathe.'}},
  'gathering':'The last binding cord is trimmed. Where loose papers once occupied every flat surface, there is now an arrangement someone can actually explain. Its compromises are visible—and deliberate.',
  'clue':'The repaired catalogue fittings suggest a place to look for the uncatalogued leaf mentioned by the old hearth records. Reading it requires actual archive study and investigation; a useful arrangement is not evidence by itself.',
  'ending':'The archive has acquired a habit: unfinished work now has a place to return to. The old leaf makes that ordinary courtesy feel less accidental.'},
 'cultivation': {
  'title':'A dependable kitchen garden','room':'conservatory','site':'old-waterworks','approach':'survey','research':None,
  'cost':18,'inputs':{'porous-clay':2,'silver-ivy':2},'work':6,'advisers':['zahra','sylva','neris','koharu'],
  'proposal':'The conservatory can grow things again. A dependable household garden needs another kind of care: channels that can be inspected and a clear decision about what the beds are for.',
  'voice':'“A garden can feed the stores or the household purse. Let us choose what these beds should do before we fill every inch.”',
  'field':'Survey the old waterworks and return with Water guidance. The measured channels will determine how the new growing benches receive water.',
  'complication':'The planting plan uses every sunny ledge for useful ivy. There would be little room for varied kitchen crops or surplus baskets. The same water supply can support either arrangement; the keeper needs a clear priority.',
  'designs':{
   'nursery':{'name':'Botanical propagation beds','description':'Shallow clay channels feed closely arranged propagation trays. A clear inspection path runs between the useful ivy beds.','benefit':'+1 silver ivy per staffed ivy harvest. No bonus to sales or unattended root-tender harvests.','effect':'ivy','amount':1,'response':'You keep the inspection path and dedicate the sunniest trays to healthy cuttings. The garden will support the workbench first.'},
   'kitchen':{'name':'Kitchen plots and surplus bench','description':'Mixed kitchen beds surround a modest sorting bench and reusable baskets, leaving less space for botanical propagation.','benefit':'+2 crowns per staffed surplus harvest. No bonus to ivy or unattended root-tender harvests.','effect':'garden-sales','amount':2,'response':'You break up the long propagation rows and make room for varied beds and sorting baskets. Useful surplus will help pay for the household’s other plans.'}},
  'gathering':'Water reaches the farthest tray without overflowing the nearest one. The growing room feels less like a collection of hopeful pots and more like a place someone could tend tomorrow.',
  'clue':'Comparing the restored beds with the hearth records raises a question about the people who once used the sleeping wing. The uncatalogued leaf is the next source to examine, after arranging the archive.',
  'ending':'The garden has a purpose its keeper can name. The old leaf suggests that making room for people and keeping a productive household were once questions asked together.'},
 'craftsmanship': {
  'title':'A working commission bench','room':'workshop','site':'old-waterworks','approach':'salvage','research':None,
  'cost':20,'inputs':{'fireglass':1,'binding-thread':2},'work':6,'advisers':['koharu','kaede','zahra','tamsin'],
  'proposal':'A fitted workshop could serve more than urgent repairs. With dependable light and a sensible bench, people could finish useful work here and still keep space for an idea of their own.',
  'voice':'“There is nothing wrong with a productive bench. There is something wrong with having nowhere to put the thing you are making just because you like it.”',
  'field':'Recover loose components from the old waterworks. One of its fireglass lenses can become the bench’s dependable working light; bring the salvage home before committing it.',
  'complication':'The production plan puts every tool within reach of a single uninterrupted assembly run. It leaves nowhere for private sketches or customer records. Do you keep the fast assembly line, or shorten it to make an alcove for drawings and commission paperwork?',
  'designs':{
   'production':{'name':'Continuous assembly bench','description':'A long fitted bench has sorted component trays and an enclosed fireglass worklight. Personal designs have to be put away between production runs.','benefit':'+1 work per assigned core-artifact crafter, in addition to the restored workshop bonus. Public-pack projects keep their own rates.','effect':'craft','amount':1,'response':'You keep the uninterrupted bench. The room will be very good at finishing things, and you agree to keep its limitations visible rather than call them everybody’s preference.'},
   'alcove':{'name':'Maker’s alcove and commission desk','description':'The shorter assembly bench shares its fireglass light with a small drawing desk, personal shelves and a tray for correspondence.','benefit':'+2 crowns per assigned founder copying phase through commission records. The ordinary workshop crafting bonus remains.','effect':'copy','amount':2,'response':'You shorten the run of trays and fit a desk under the same light. Personal sketches can stay open while the next commission takes shape.'}},
  'gathering':'Tools go back to places chosen for them. A first set of work notes can stay on the desk instead of being moved to make room for supper. The workshop finally has a rhythm beyond the next emergency.',
  'clue':'A comparison between the new bench records and the hearth mark points back to the uncatalogued household leaf. Arrange the archive and investigate it before deciding what the old workshop meant.',
  'ending':'The bench is useful because of the work actually done at it. The old leaf puts the visiting craftspeople back into the house’s history, alongside the tools they used.'}
}
PURPOSES={
 'practical':('Give useful work a dependable home','You agree to judge the project by what someone can actually do here. Its costs, work and results belong on the same page.'),
 'welcome':('Leave room for the people doing the work','You put a second question beside the measurements: who will find this space comfortable to use? The answer should survive the final fitting.')}
CLOSINGS={
 'credit':('Name the contributions','You record who actually worked on the fitting, keeping advice distinct from hours at the bench. Nobody acquires an obligation merely by being thanked.'),
 'enjoy':('Enjoy the room before planning more','You leave the next list unopened. There is a little time to notice what this room has become before asking it to become anything else.')}
