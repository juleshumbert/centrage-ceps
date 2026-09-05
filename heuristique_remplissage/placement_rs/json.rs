// Lecteur / ecrivain JSON minimal, sans dependance.
use std::collections::BTreeMap;

#[derive(Debug, Clone)]
pub enum Json {
    Null,
    Bool(bool),
    Num(f64),
    Str(String),
    Arr(Vec<Json>),
    Obj(BTreeMap<String, Json>),
}

impl Json {
    pub fn get(&self, k: &str) -> Option<&Json> {
        match self {
            Json::Obj(m) => m.get(k),
            _ => None,
        }
    }
    pub fn num(&self) -> Option<f64> {
        match self {
            Json::Num(v) => Some(*v),
            _ => None,
        }
    }
    pub fn str(&self) -> Option<&str> {
        match self {
            Json::Str(s) => Some(s),
            _ => None,
        }
    }
    pub fn boolean(&self) -> Option<bool> {
        match self {
            Json::Bool(b) => Some(*b),
            _ => None,
        }
    }
    pub fn arr(&self) -> Option<&Vec<Json>> {
        match self {
            Json::Arr(a) => Some(a),
            _ => None,
        }
    }
    pub fn dump(&self) -> String {
        let mut s = String::new();
        self.write(&mut s, 0);
        s
    }
    fn write(&self, out: &mut String, indent: usize) {
        match self {
            Json::Null => out.push_str("null"),
            Json::Bool(b) => out.push_str(if *b { "true" } else { "false" }),
            Json::Num(v) => {
                if v.is_finite() {
                    if (v.fract() == 0.0) && v.abs() < 1e15 {
                        out.push_str(&format!("{}", *v as i64));
                    } else {
                        out.push_str(&format!("{}", (v * 1e4).round() / 1e4));
                    }
                } else {
                    out.push_str("null");
                }
            }
            Json::Str(s) => {
                out.push('"');
                for c in s.chars() {
                    match c {
                        '"' => out.push_str("\\\""),
                        '\\' => out.push_str("\\\\"),
                        '\n' => out.push_str("\\n"),
                        _ => out.push(c),
                    }
                }
                out.push('"');
            }
            Json::Arr(a) => {
                if a.is_empty() {
                    out.push_str("[]");
                    return;
                }
                let simple = a.iter().all(|v| !matches!(v, Json::Arr(_) | Json::Obj(_)));
                out.push('[');
                for (i, v) in a.iter().enumerate() {
                    if i > 0 {
                        out.push_str(", ");
                    }
                    if !simple {
                        out.push('\n');
                        out.push_str(&" ".repeat(indent + 1));
                    }
                    v.write(out, indent + 1);
                }
                if !simple {
                    out.push('\n');
                    out.push_str(&" ".repeat(indent));
                }
                out.push(']');
            }
            Json::Obj(m) => {
                out.push('{');
                for (i, (k, v)) in m.iter().enumerate() {
                    if i > 0 {
                        out.push(',');
                    }
                    out.push('\n');
                    out.push_str(&" ".repeat(indent + 1));
                    out.push_str(&format!("\"{}\": ", k));
                    v.write(out, indent + 1);
                }
                out.push('\n');
                out.push_str(&" ".repeat(indent));
                out.push('}');
            }
        }
    }
}

pub fn obj(pairs: Vec<(&str, Json)>) -> Json {
    let mut m = BTreeMap::new();
    for (k, v) in pairs {
        m.insert(k.to_string(), v);
    }
    Json::Obj(m)
}

struct P<'a> {
    s: &'a [u8],
    i: usize,
}

impl<'a> P<'a> {
    fn ws(&mut self) {
        while self.i < self.s.len() && (self.s[self.i] as char).is_whitespace() {
            self.i += 1;
        }
    }
    fn err(&self, m: &str) -> String {
        format!("JSON : {} a la position {}", m, self.i)
    }
    fn value(&mut self) -> Result<Json, String> {
        self.ws();
        if self.i >= self.s.len() {
            return Err(self.err("fin inattendue"));
        }
        match self.s[self.i] {
            b'{' => {
                self.i += 1;
                let mut m = BTreeMap::new();
                loop {
                    self.ws();
                    if self.i < self.s.len() && self.s[self.i] == b'}' {
                        self.i += 1;
                        break;
                    }
                    let k = match self.value()? {
                        Json::Str(s) => s,
                        _ => return Err(self.err("cle attendue")),
                    };
                    self.ws();
                    if self.i >= self.s.len() || self.s[self.i] != b':' {
                        return Err(self.err("':' attendu"));
                    }
                    self.i += 1;
                    let v = self.value()?;
                    m.insert(k, v);
                    self.ws();
                    if self.i < self.s.len() && self.s[self.i] == b',' {
                        self.i += 1;
                    }
                }
                Ok(Json::Obj(m))
            }
            b'[' => {
                self.i += 1;
                let mut a = Vec::new();
                loop {
                    self.ws();
                    if self.i < self.s.len() && self.s[self.i] == b']' {
                        self.i += 1;
                        break;
                    }
                    a.push(self.value()?);
                    self.ws();
                    if self.i < self.s.len() && self.s[self.i] == b',' {
                        self.i += 1;
                    }
                }
                Ok(Json::Arr(a))
            }
            b'"' => {
                self.i += 1;
                let mut out = String::new();
                while self.i < self.s.len() && self.s[self.i] != b'"' {
                    if self.s[self.i] == b'\\' {
                        self.i += 1;
                        let c = self.s[self.i];
                        match c {
                            b'n' => out.push('\n'),
                            b't' => out.push('\t'),
                            b'u' => {
                                let h = std::str::from_utf8(&self.s[self.i + 1..self.i + 5]).unwrap_or("0000");
                                out.push(char::from_u32(u32::from_str_radix(h, 16).unwrap_or(63)).unwrap_or('?'));
                                self.i += 4;
                            }
                            _ => out.push(c as char),
                        }
                        self.i += 1;
                    } else {
                        // utf-8 : copier l'octet tel quel
                        let start = self.i;
                        let len = utf8_len(self.s[self.i]);
                        out.push_str(std::str::from_utf8(&self.s[start..start + len]).unwrap_or("?"));
                        self.i += len;
                    }
                }
                self.i += 1;
                Ok(Json::Str(out))
            }
            b't' => { self.i += 4; Ok(Json::Bool(true)) }
            b'f' => { self.i += 5; Ok(Json::Bool(false)) }
            b'n' => { self.i += 4; Ok(Json::Null) }
            _ => {
                let start = self.i;
                while self.i < self.s.len() && (b"+-.eE0123456789".contains(&self.s[self.i])) {
                    self.i += 1;
                }
                let t = std::str::from_utf8(&self.s[start..self.i]).unwrap_or("");
                t.parse::<f64>().map(Json::Num).map_err(|_| self.err("nombre attendu"))
            }
        }
    }
}

fn utf8_len(b: u8) -> usize {
    if b < 0x80 { 1 } else if b >> 5 == 0b110 { 2 } else if b >> 4 == 0b1110 { 3 } else { 4 }
}

pub fn parse(text: &str) -> Result<Json, String> {
    let mut p = P { s: text.as_bytes(), i: 0 };
    p.value()
}
