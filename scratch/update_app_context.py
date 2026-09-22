import re

with open('src/context/AppContext.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

get_officer_base_func = '''
  const getOfficerApiBase = (modOverride) => {
    const mod = (modOverride || activeModule || localStorage.getItem('sda_active_module') || 'criminal-tracking').toLowerCase();
    if (mod === 'missing-child' || mod === 'missing_child' || mod === 'missing-children') return { url: '/api/missing-children/authority-information', isAuth: true };
    if (mod === 'criminal-tracking' || mod === 'criminal') return { url: '/api/criminal/officer_information', isAuth: true };
    return { url: null, isAuth: false };
  };
'''

content = content.replace('  const fetchOfficers = async () => {', get_officer_base_func + '\n  const fetchOfficers = async () => {')

m_fetch = re.search(r'const currentMod =.*?if \(!isCriminalMod\) \{.*?return;\n    \}', content, re.DOTALL)
if m_fetch:
    content = content.replace(m_fetch.group(0), 'const officerApi = getOfficerApiBase();\n    if (!officerApi.isAuth || !officerApi.url) {\n      isFetchingOfficersRef.current = false;\n      return;\n    }')
content = content.replace("'http://127.0.0.1:8000/api/criminal/officer_information'", "officerApi.url")

m_add = re.search(r"const res = await authFetch\('http://127\.0\.0\.1:8000/api/criminal/officer_information', \{", content)
if m_add:
    content = content.replace(m_add.group(0), "const officerApi = getOfficerApiBase();\n      if (!officerApi.url) return;\n      const res = await authFetch(officerApi.url, {")

m_upd = re.search(r"const res = await authFetch\(`http://127\.0\.0\.1:8000/api/criminal/officer_information/\$\{docId\}`", content)
if m_upd:
    content = content.replace(m_upd.group(0), "const officerApi = getOfficerApiBase();\n      if (!officerApi.url) return;\n      const res = await authFetch(`${officerApi.url}/${docId}`")

m_del = re.search(r"const res = await authFetch\(`http://127\.0\.0\.1:8000/api/criminal/officer_information/\$\{docId\}`", content)
if m_del:
    content = content.replace(m_del.group(0), "const officerApi = getOfficerApiBase();\n      if (!officerApi.url) return;\n      const res = await authFetch(`${officerApi.url}/${docId}`")

m_init_off = re.search(r"token && isCriminalMod \? authFetch\('/api/criminal/officer_information'\).*?Promise\.resolve\(null\)", content)
if m_init_off:
    content = content.replace(m_init_off.group(0), "token && getOfficerApiBase(activeMod).isAuth ? authFetch(getOfficerApiBase(activeMod).url).then(res => res && res.ok ? res.json() : null).catch(() => null) : Promise.resolve(null)")

with open('src/context/AppContext.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
