/**
 * fNIRS Lab Equipment Scheduler — Apps Script backend
 * ----------------------------------------------------
 * Deploy this bound to a Google Sheet with three tabs:
 *
 *   Equipment          id | category | num | label | sub | size | status | notes | serial
 *   Reservations       id | userName | userEmail | project | start | end | purpose | status | createdAt
 *   ReservationItems   reservationId | itemId
 *
 * Row 1 of each tab must be exactly those header names (case-sensitive).
 * Everything below this comment is the whole backend — no other files needed.
 *
 * SETUP
 * 1. Paste your Sheet's ID (from its URL, the long string between /d/ and /edit)
 *    into SHEET_ID below.
 * 2. Deploy > New deployment > type "Web app".
 *      Execute as:  Me
 *      Who has access:  Anyone
 * 3. Copy the deployment's /exec URL into APPS_SCRIPT_URL in the front-end
 *    (index.html, near the top of the <script> block).
 * 4. Every time you edit this file, use Deploy > Manage deployments > edit
 *    (pencil icon) > New version, or the URL will keep serving old code.
 */

const SHEET_ID = 'PASTE_YOUR_SHEET_ID_HERE';

const EQUIPMENT_SHEET = 'Equipment';
const RESERVATIONS_SHEET = 'Reservations';
const ITEMS_SHEET = 'ReservationItems';

const EQUIPMENT_HEADERS = ['id','category','num','label','sub','size','status','notes','serial'];
const RESERVATIONS_HEADERS = ['id','userName','userEmail','project','start','end','purpose','status','createdAt'];
const ITEMS_HEADERS = ['reservationId','itemId'];

// Standard catalog, used only to seed a brand-new Equipment sheet on first run.
const SEED_CATALOG = [
  ...range(1,5).map(n => ({id:`U${n}`, category:'unit', num:n, label:`NIRSport2 Unit ${n}`, sub:'', size:'', serial:`NX2-2024-0${n}`})),
  ...range(1,7).map(n => ({id:`S${n}`, category:'source', num:n, label:`Red Source Bundle ${n}`, sub:'', size:'', serial:`RSB-${100+n}`})),
  ...range(1,7).map(n => ({id:`D${n}`, category:'detector', num:n, label:`Blue Detector Bundle ${n}`, sub:'', size:'', serial:`BDB-${100+n}`})),
  ...range(1,7).map(n => ({id:`H${n}`, category:'headband', num:n, label:`Headband ${n}`, sub:'', size:'', serial:`HB-${100+n}`})),
  ...capSeed(),
  ...range(1,9).map(n => ({id:`L${n}`, category:'laptop', num:n, label:`fNIRS ${n}`, sub:'', size:'', serial:`LT-fNIRS-0${n}`})),
  ...range(1,2).map(n => ({id:`R${n}`, category:'network', num:n, label:`Router ${n}`, sub:'', size:'', serial:`RTR-0${n}`})),
  { id:'CAB1', category:'storage', num:1, label:'Rolling Cabinet', sub:'', size:'', serial:'CAB-01' },
];

function range(a,b){ const out=[]; for(let i=a;i<=b;i++) out.push(i); return out; }
function capSeed(){
  const sizes = [52,52,54,54,54,54,56,56,56,56,56,56,58,58,58,58,60,60];
  return sizes.map((size,idx)=>{
    const n = idx+1;
    return { id:`C${n}`, category:'cap', num:n, label:`Cap ${n}`, sub:`${size} cm`, size, serial:`CAP-${n}` };
  });
}

/* ---------------- entry points ---------------- */

function doGet(e){
  ensureSheetsExist();
  seedEquipmentIfEmpty();
  const equipment = sheetToObjects(sheet(EQUIPMENT_SHEET));
  const reservationsRaw = sheetToObjects(sheet(RESERVATIONS_SHEET));
  const itemLinks = sheetToObjects(sheet(ITEMS_SHEET));
  const reservations = reservationsRaw.map(r => Object.assign({}, r, {
    items: itemLinks.filter(link => link.reservationId === r.id).map(link => link.itemId)
  }));
  return jsonOut({ ok:true, equipment, reservations });
}

function doPost(e){
  const lock = LockService.getScriptLock();
  try{
    lock.waitLock(15000); // serializes writes so two people can't take the same item at once
  } catch(lockErr){
    return jsonOut({ ok:false, error:'The scheduler is busy — try again in a moment.' });
  }
  try{
    ensureSheetsExist();
    const body = JSON.parse(e.postData.contents);
    switch(body.action){
      case 'reserve': return jsonOut(handleReserve(body));
      case 'cancel': return jsonOut(handleCancel(body));
      case 'addEquipment': return jsonOut(handleAddEquipment(body));
      case 'toggleMaintenance': return jsonOut(handleToggleMaintenance(body));
      default: return jsonOut({ ok:false, error:'Unknown action: ' + body.action });
    }
  } catch(err){
    return jsonOut({ ok:false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

/* ---------------- action handlers ---------------- */

function handleReserve(body){
  const { userName, userEmail, project, start, end, purpose, items } = body;
  if(!userName || !project || !start || !end || !items || !items.length){
    return { ok:false, error:'Missing required fields.' };
  }
  const existing = sheetToObjects(sheet(RESERVATIONS_SHEET)).filter(r=>r.status==='active');
  const itemLinks = sheetToObjects(sheet(ITEMS_SHEET));
  const s = new Date(start), en = new Date(end);

  const conflicts = [];
  items.forEach(itemId=>{
    const bookedIds = itemLinks.filter(l=>l.itemId===itemId).map(l=>l.reservationId);
    existing.forEach(r=>{
      if(!bookedIds.includes(r.id)) return;
      if(overlaps(s,en,new Date(r.start),new Date(r.end))){
        conflicts.push({ itemId, byName:r.userName, start:r.start, end:r.end });
      }
    });
  });
  if(conflicts.length){
    return { ok:false, error:'Some items were just taken for this window.', conflicts };
  }

  const id = 'R-' + Utilities.getUuid().slice(0,8).toUpperCase();
  const createdAt = new Date().toISOString();
  sheet(RESERVATIONS_SHEET).appendRow([id, userName, userEmail||'', project, start, end, purpose||'', 'active', createdAt]);
  const itemSheet = sheet(ITEMS_SHEET);
  items.forEach(itemId => itemSheet.appendRow([id, itemId]));

  return { ok:true, reservation:{ id, userName, userEmail, project, start, end, purpose, status:'active', createdAt, items } };
}

function handleCancel(body){
  const { reservationId } = body;
  const sh = sheet(RESERVATIONS_SHEET);
  const rows = sh.getDataRange().getValues();
  const idCol = RESERVATIONS_HEADERS.indexOf('id');
  const statusCol = RESERVATIONS_HEADERS.indexOf('status');
  for(let i=1;i<rows.length;i++){
    if(rows[i][idCol] === reservationId){
      sh.getRange(i+1, statusCol+1).setValue('cancelled');
      return { ok:true };
    }
  }
  return { ok:false, error:'Reservation not found.' };
}

function handleAddEquipment(body){
  const { id, category, num, label, sub, size, notes } = body;
  if(!id || !category || !label) return { ok:false, error:'Missing required fields.' };
  const existing = sheetToObjects(sheet(EQUIPMENT_SHEET));
  if(existing.some(e=>e.id===id)) return { ok:false, error: id + ' already exists.' };
  sheet(EQUIPMENT_SHEET).appendRow([id, category, num, label, sub||'', size||'', 'active', notes||'', id+'-NEW']);
  return { ok:true };
}

function handleToggleMaintenance(body){
  const { itemId } = body;
  const sh = sheet(EQUIPMENT_SHEET);
  const rows = sh.getDataRange().getValues();
  const idCol = EQUIPMENT_HEADERS.indexOf('id');
  const statusCol = EQUIPMENT_HEADERS.indexOf('status');
  for(let i=1;i<rows.length;i++){
    if(rows[i][idCol] === itemId){
      const next = rows[i][statusCol] === 'active' ? 'maintenance' : 'active';
      sh.getRange(i+1, statusCol+1).setValue(next);
      return { ok:true, status: next };
    }
  }
  return { ok:false, error:'Item not found.' };
}

/* ---------------- sheet helpers ---------------- */

function ss(){ return SpreadsheetApp.openById(SHEET_ID); }
function sheet(name){ return ss().getSheetByName(name); }

function ensureSheetsExist(){
  const book = ss();
  if(!book.getSheetByName(EQUIPMENT_SHEET)){ const s=book.insertSheet(EQUIPMENT_SHEET); s.appendRow(EQUIPMENT_HEADERS); }
  if(!book.getSheetByName(RESERVATIONS_SHEET)){ const s=book.insertSheet(RESERVATIONS_SHEET); s.appendRow(RESERVATIONS_HEADERS); }
  if(!book.getSheetByName(ITEMS_SHEET)){ const s=book.insertSheet(ITEMS_SHEET); s.appendRow(ITEMS_HEADERS); }
}

function seedEquipmentIfEmpty(){
  const sh = sheet(EQUIPMENT_SHEET);
  if(sh.getLastRow() > 1) return; // already has data beyond the header row
  SEED_CATALOG.forEach(item=>{
    sh.appendRow([item.id, item.category, item.num, item.label, item.sub, item.size, 'active', '', item.serial]);
  });
}

function sheetToObjects(sh){
  const values = sh.getDataRange().getValues();
  if(values.length < 2) return [];
  const headers = values[0];
  return values.slice(1)
    .filter(row => row.some(cell => cell !== '' && cell !== null))
    .map(row=>{
      const obj = {};
      headers.forEach((h,i)=>{
        let v = row[i];
        if(v instanceof Date) v = v.toISOString();
        obj[h] = v;
      });
      return obj;
    });
}

function overlaps(aStart,aEnd,bStart,bEnd){
  return aStart < bEnd && bStart < aEnd;
}

function jsonOut(obj){
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
