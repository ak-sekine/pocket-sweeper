from pathlib import Path
import sys, re
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
sys.path.insert(0,str(Path(__file__).parent)); from validate_wbs import validate

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'reports/wbs.xlsx'
def main():
    data,issues=validate()
    if any(x[0]=='error' for x in issues):
        print('WBS validation failed; Excel was not generated',file=sys.stderr); return 1
    rows=list(data.values()); children={i:[] for i in data}
    for ident,(_,m,_) in data.items():
        if m.get('parent') in children: children[m['parent']].append(ident)
    order=[]
    def visit(i,level=0):
        order.append((i,level));
        for c in children[i]: visit(c,level+1)
    for i,(_,m,_) in data.items():
        if not m.get('parent'): visit(i)
    def val(m,k):
        x=m.get(k); return ', '.join(map(str,x)) if isinstance(x,list) else (x or '')
    wb=Workbook(); ws=wb.active; ws.title='WBS一覧'
    headers=['WBS ID','プロジェクト番号','プロジェクト内番号','親WBS ID','階層','種別','WBS名','担当','状態','依存先','流用元WBS','仕様書','関連ファイル','成果物','ブロック理由','完了条件要約','証跡要約','更新日','詳細ファイル']
    ws.append(headers)
    for ident,level in order:
        path,m,text=data[ident]; ws.append([ident,ident[4:7],ident[8:],m.get('parent') or '',level,m.get('type'),m.get('title'),m.get('actor'),m.get('status'),val(m,'depends_on'),val(m,'source_wbs'),val(m,'specs'),val(m,'related_files'),val(m,'outputs'),val(m,'blocked_by'),'既存項目を完了し証跡を記録する' if m.get('type')=='task' else '', '移行時点の状態を保存',m.get('updated'),str(path.relative_to(ROOT))])
    ws2=wb.create_sheet('未完了一覧'); ws2.append(['WBS ID','WBS名','担当','親WBS ID','依存先','ブロック理由','完了条件要約','詳細ファイル'])
    for ident,(_,m,_) in data.items():
        if m.get('type')=='task' and m.get('status')=='incomplete': ws2.append([ident,m.get('title'),m.get('actor'),m.get('parent') or '',val(m,'depends_on'),val(m,'blocked_by'),'既存項目を完了し証跡を記録する',str(Path('wbs/tasks')/(ident+'.md'))])
    tasks=[m for _,m,_ in rows]; done=[m for m in tasks if m.get('type')=='task' and m.get('status')=='complete']; execs=[m for m in tasks if m.get('type')=='task']
    ws3=wb.create_sheet('進捗集計'); ws3.append(['項目','値']); stats=[('実行タスク総数',len(execs)),('完了タスク数',len(done)),('未完了タスク数',len(execs)-len(done)),('完了率',len(done)/len(execs) if execs else 0),('Codex担当タスク数',sum(m.get('actor')=='codex' for m in execs)),('Codex担当の未完了数',sum(m.get('actor')=='codex' and m.get('status')!='complete' for m in execs)),('人担当タスク数',sum(m.get('actor')=='human' for m in execs)),('人担当の未完了数',sum(m.get('actor')=='human' and m.get('status')!='complete' for m in execs)),('担当未確定数',sum(m.get('actor_review_required',False) for m in tasks)),('グループ数',sum(m.get('type')=='group' for m in tasks))];
    for x in stats: ws3.append(x)
    ws4=wb.create_sheet('検証結果'); ws4.append(['種別','WBS ID','ファイル','内容']);
    for x in issues: ws4.append(x)
    ws5=wb.create_sheet('移行対応'); ws5.append(['旧階層パス','新WBS ID','種別','担当','状態','分割・統合情報','備考'])
    for ident,level in order:
        _,m,_=data[ident]; ws5.append([f"深さ{level}: {m.get('title')}",ident,m.get('type'),m.get('actor'),m.get('status'),'なし','PROJECT.md出現順で移行'])
    for sheet in wb.worksheets:
        sheet.freeze_panes='A2'; sheet.auto_filter.ref=sheet.dimensions
        for cell in sheet[1]: cell.font=Font(bold=True,color='FFFFFF'); cell.fill=PatternFill('solid',fgColor='1F4E78'); cell.alignment=Alignment(wrap_text=True)
        for row in sheet.iter_rows():
            for c in row: c.alignment=Alignment(vertical='top',wrap_text=True)
        for i in range(1,sheet.max_column+1): sheet.column_dimensions[get_column_letter(i)].width=min(42,max(12,max(len(str(sheet.cell(r,i).value or '')) for r in range(1,min(sheet.max_row,40)+1))+2))
    OUT.parent.mkdir(exist_ok=True); wb.save(OUT); print(OUT); return 0
if __name__=='__main__': sys.exit(main())
