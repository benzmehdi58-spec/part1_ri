"""
Module NLP Pipeline - Implementation 100% From Scratch
Sans NLTK, spaCy, ni expressions regulieres complexes (module re).
Toutes les operations utilisent exclusivement la manipulation de chaines
et dictionnaires natifs Python.
"""

import string
from typing import List, Dict, Set, Union, Optional


# =============================================================================
# 1. Nettoyage des balises SGML / XML
# =============================================================================

def tag_cleaning(text: str) -> str:
    """
    Supprime manuellement les balises SGML/XML et entites du texte.
    Methode : Automate d'etat a balayage caractere par caractere.
    """
    clean_chars = []
    inside_tag = False

    for ch in text:
        if ch == '<':
            inside_tag = True
        elif ch == '>':
            inside_tag = False
            clean_chars.append(' ')
        elif not inside_tag:
            clean_chars.append(ch)

    result = ''.join(clean_chars)

    # Remplacement des entites SGML / HTML et caracteres de controle Reuters
    entities = {
        '&lt;': '<',
        '&gt;': '>',
        '&amp;': '&',
        '&quot;': '"',
        '&apos;': "'",
        '&#2;': '',
        '&#3;': '',
        '&#5;': '',
        '&#22;': '',
        '&nbsp;': ' ',
        '\x02': '',
        '\x03': '',
    }
    for ent, repl in entities.items():
        result = result.replace(ent, repl)

    return result


# =============================================================================
# 2. Normalisation et Tokenisation
# =============================================================================

def normalization(text: str) -> List[str]:
    """
    Normalise le texte en minuscules, retire la ponctuation et decoupe en tokens.
    Methode : str.lower + str.translate (sans regex).
    Conserve les tokens d'au moins 2 caracteres comportant au moins une lettre.
    """
    text_lower = text.lower()

    punct_chars = (
        string.punctuation +
        chr(171) + chr(187) + chr(8220) + chr(8221) +
        chr(8216) + chr(8217) + chr(8212) + chr(8211) +
        chr(8230) + '\t\r\n'
    )
    trans_table = str.maketrans(punct_chars, ' ' * len(punct_chars))
    cleaned = text_lower.translate(trans_table)

    raw_tokens = cleaned.split()
    tokens = []
    for tok in raw_tokens:
        tok_clean = tok.strip()
        if len(tok_clean) >= 2 and any(c.isalpha() for c in tok_clean):
            tokens.append(tok_clean)

    return tokens


# =============================================================================
# 3. Suppression des Mots Vides (Stopwords Removal)
# =============================================================================

DEFAULT_STOPWORDS: Set[str] = {
    # Mots fonctionnels anglais courants
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'almost',
    'also', 'although', 'always', 'am', 'among', 'an', 'and', 'another',
    'any', 'are', 'around', 'as', 'at', 'be', 'became', 'because', 'become',
    'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
    'can', 'cannot', 'could', 'did', 'do', 'does', 'doing', 'done', 'down',
    'during', 'each', 'either', 'even', 'every', 'few', 'first', 'for',
    'from', 'further', 'had', 'has', 'have', 'having', 'he', 'her', 'here',
    'hers', 'him', 'his', 'how', 'however', 'i', 'if', 'in', 'into', 'is',
    'it', 'its', 'itself', 'just', 'made', 'many', 'may', 'me', 'might',
    'more', 'most', 'much', 'must', 'my', 'neither', 'no', 'nor', 'not',
    'now', 'of', 'off', 'often', 'on', 'once', 'one', 'only', 'or', 'other',
    'our', 'out', 'over', 'own', 'per', 'put', 'same', 'see', 'several',
    'she', 'should', 'since', 'so', 'some', 'still', 'such', 'than', 'that',
    'the', 'their', 'them', 'then', 'there', 'these', 'they', 'this', 'those',
    'through', 'to', 'too', 'under', 'until', 'up', 'us', 'very', 'was', 'we',
    'well', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom',
    'why', 'will', 'with', 'within', 'without', 'would',
    # Bruit specifique au corpus Reuters
    'reuter', 'reuters', 'said', 'says', 'say', 'year', 'years',
    'mln', 'bln', 'dlrs', 'cts', 'pct', 'lt', 'inc', 'corp', 'co',
    'week', 'month', 'day', 'days', 'last', 'next', 'new', 'old',
    'ago', 'january', 'february', 'march', 'june', 'july',
    'august', 'september', 'october', 'november', 'december',
    'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
    'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
}


def remove_stopwords(tokens: List[str], stopwords: Optional[Set[str]] = None) -> List[str]:
    """Filtre les mots figurant dans la liste des stopwords."""
    if stopwords is None:
        stopwords = DEFAULT_STOPWORDS
    return [tok for tok in tokens if tok not in stopwords]


# =============================================================================
# 4. Racinisation (Stemming) - Algorithme Manuel type Porter
# =============================================================================

def stem_word(word: str) -> str:
    """
    Racinisation manuelle par suffix-stripping.
    Aucune bibliotheque externe.
    """
    w = word.lower()
    if len(w) <= 3:
        return w

    # Regle 1 : Pluriels et 3e personne
    if w.endswith('sses'):
        w = w[:-2]
    elif w.endswith('ies') and len(w) > 4:
        w = w[:-2]
    elif w.endswith('ss'):
        pass
    elif w.endswith('es') and len(w) > 4:
        w = w[:-2]
    elif w.endswith('s') and len(w) > 3:
        if not w.endswith(('us', 'is', 'ss')):
            w = w[:-1]

    # Regle 2 : Formes passees
    if len(w) > 4 and w.endswith('eed'):
        w = w[:-1]
    elif len(w) > 4 and w.endswith('ed'):
        stem = w[:-2]
        if len(stem) >= 3:
            if len(stem) >= 2 and stem[-1] == stem[-2] and stem[-1] not in ('l', 's', 'z'):
                stem = stem[:-1]
            w = stem

    # Regle 3 : Participe present
    if len(w) > 5 and w.endswith('ing'):
        stem = w[:-3]
        if len(stem) >= 3:
            if len(stem) >= 2 and stem[-1] == stem[-2] and stem[-1] not in ('l', 's', 'z'):
                stem = stem[:-1]
            w = stem

    # Regles 4 & 5 : Suffixes derivationnels
    if len(w) > 4 and w.endswith('ly'):
        w = w[:-2]
    elif len(w) > 6 and w.endswith('ment'):
        w = w[:-4]
    elif len(w) > 6 and w.endswith('ness'):
        w = w[:-4]
    elif len(w) > 6 and w.endswith('ful'):
        w = w[:-3]
    elif len(w) > 6 and w.endswith('able'):
        w = w[:-4]
    elif len(w) > 6 and w.endswith('ible'):
        w = w[:-4]
    elif len(w) > 6 and w.endswith('tion'):
        w = w[:-3]  # ex: production -> product
    elif len(w) > 6 and w.endswith('sion'):
        w = w[:-3]
    elif len(w) > 5 and w.endswith('al'):
        w = w[:-2]

    return w


def stemming(tokens: Union[List[str], str]) -> List[str]:
    """Applique stem_word a chaque token."""
    if isinstance(tokens, str):
        tokens = [tokens]
    return [stem_word(t) for t in tokens]


# =============================================================================
# 5. Lemmatisation (Lemmatization) - Dictionnaire manuel
# =============================================================================

DEFAULT_LEMMA_DICT: Dict[str, str] = {
    # Auxiliaires
    'is': 'be', 'am': 'be', 'are': 'be', 'was': 'be',
    'were': 'be', 'been': 'be', 'being': 'be',
    'has': 'have', 'had': 'have', 'having': 'have',
    'does': 'do', 'did': 'do', 'done': 'do', 'doing': 'do',

    # Verbes de declaration & finance
    'says': 'say', 'said': 'say', 'saying': 'say',
    'reports': 'report', 'reported': 'report', 'reporting': 'report',
    'expects': 'expect', 'expected': 'expect', 'expecting': 'expect',
    'plans': 'plan', 'planned': 'plan', 'planning': 'plan',
    'rises': 'rise', 'rose': 'rise', 'risen': 'rise', 'rising': 'rise',
    'falls': 'fall', 'fell': 'fall', 'fallen': 'fall', 'falling': 'fall',
    'grows': 'grow', 'grew': 'grow', 'grown': 'grow', 'growing': 'grow',
    'declines': 'decline', 'declined': 'decline', 'declining': 'decline',
    'increases': 'increase', 'increased': 'increase', 'increasing': 'increase',
    'dropped': 'drop', 'drops': 'drop', 'dropping': 'drop',
    'gained': 'gain', 'gains': 'gain', 'gaining': 'gain',
    'buys': 'buy', 'bought': 'buy', 'buying': 'buy',
    'sells': 'sell', 'sold': 'sell', 'selling': 'sell',
    'pays': 'pay', 'paid': 'pay', 'paying': 'pay',
    'makes': 'make', 'made': 'make', 'making': 'make',
    'invests': 'invest', 'invested': 'invest', 'investing': 'invest',
    'traded': 'trade', 'trades': 'trade', 'trading': 'trade',
    'raised': 'raise', 'raises': 'raise', 'raising': 'raise',
    'cut': 'cut', 'cuts': 'cut', 'cutting': 'cut',
    'borrowed': 'borrow', 'borrows': 'borrow', 'borrowing': 'borrow',
    'lent': 'lend', 'lends': 'lend', 'lending': 'lend',
    'approved': 'approve', 'approves': 'approve', 'approving': 'approve',
    'announced': 'announce', 'announces': 'announce', 'announcing': 'announce',
    'closed': 'close', 'closes': 'close', 'closing': 'close',
    'opened': 'open', 'opens': 'open', 'opening': 'open',
    'merged': 'merge', 'merges': 'merge', 'merging': 'merge',
    'acquired': 'acquire', 'acquires': 'acquire', 'acquiring': 'acquire',
    'produced': 'produce', 'produces': 'produce', 'producing': 'produce',
    'supplied': 'supply', 'supplies': 'supply', 'supplying': 'supply',
    'demanded': 'demand', 'demands': 'demand', 'demanding': 'demand',
    'exported': 'export', 'exporting': 'export',
    'imported': 'import', 'importing': 'import',

    # Noms frequents (pluriel -> singulier)
    'dollars': 'dollar', 'shares': 'share', 'stocks': 'stock',
    'prices': 'price', 'markets': 'market', 'companies': 'company',
    'countries': 'country', 'rates': 'rate', 'currencies': 'currency',
    'economies': 'economy', 'profits': 'profit', 'revenues': 'revenue',
    'losses': 'loss', 'investments': 'investment', 'investors': 'investor',
    'barrels': 'barrel', 'pipelines': 'pipeline', 'bonds': 'bond',
    'traders': 'trader', 'exports': 'export', 'imports': 'import',
    'volumes': 'volume', 'grains': 'grain', 'crops': 'crop',
    'banks': 'bank', 'funds': 'fund', 'loans': 'loan',
    'debts': 'debt', 'deficits': 'deficit', 'surpluses': 'surplus',
    'agreements': 'agreement', 'contracts': 'contract',
    'sanctions': 'sanction', 'tariffs': 'tariff',
    'governments': 'government', 'officials': 'official',
    'analysts': 'analyst', 'producers': 'producer',
    'consumers': 'consumer', 'suppliers': 'supplier',
    'buyers': 'buyer', 'sellers': 'seller',
    'workers': 'worker', 'employees': 'employee',
    'executives': 'executive', 'quarters': 'quarter',
    'sectors': 'sector', 'industries': 'industry',
    'regions': 'region', 'tonnes': 'tonne',
    'hectares': 'hectare', 'acres': 'acre',

    # Comparatifs / superlatifs
    'higher': 'high', 'highest': 'high',
    'lower': 'low', 'lowest': 'low',
    'stronger': 'strong', 'weakest': 'weak', 'weaker': 'weak',
    'larger': 'large', 'largest': 'large',
    'smaller': 'small', 'smallest': 'small',
    'cheaper': 'cheap', 'cheapest': 'cheap',
    'sharper': 'sharp', 'sharpest': 'sharp',
    'steeper': 'steep', 'steepest': 'steep',
}


def lemmatization(tokens: Union[List[str], str], lemma_dict: Optional[Dict[str, str]] = None) -> List[str]:
    """Remplace chaque token par sa forme canonique s'il figure dans lemma_dict."""
    if lemma_dict is None:
        lemma_dict = DEFAULT_LEMMA_DICT
    if isinstance(tokens, str):
        tokens = [tokens]
    return [lemma_dict.get(t, t) for t in tokens]


# =============================================================================
# 6. Classe NLPPipeline - Orchestrateur dynamique et configurable
# =============================================================================

class NLPPipeline:
    """
    Pipeline NLP dynamique : permet a l'administrateur de cocher les etapes
    et de definir leur ordre d'execution avec verification de coherence.
    """

    REGISTRY = {
        'tag_cleaning': tag_cleaning,
        'normalization': normalization,
        'stopwords': remove_stopwords,
        'stemming': stemming,
        'lemmatization': lemmatization,
    }

    STR_INPUT_STEPS = {'tag_cleaning', 'normalization'}

    def __init__(self, steps: Optional[List[str]] = None):
        default = ['tag_cleaning', 'normalization', 'stopwords', 'stemming']
        self.steps: List[str] = []
        self.set_steps(steps if steps is not None else default)

    def _validate_order(self, steps: List[str]):
        """
        Valide l'ordre d'execution pour eviter les incoherences fonctionnelles.
        """
        list_steps = {'stopwords', 'stemming', 'lemmatization'}
        seen = []
        for step in steps:
            if step in seen:
                raise ValueError(f"Etape dupliquee dans le pipeline : '{step}'")
            seen.append(step)

        if 'normalization' not in steps:
            for s in list_steps:
                if s in steps:
                    raise ValueError(
                        f"L'etape '{s}' necessite 'normalization' au prealable pour decouper en tokens."
                    )

        norm_pos = steps.index('normalization') if 'normalization' in steps else -1
        for s in list_steps:
            if s in steps:
                s_pos = steps.index(s)
                if norm_pos > s_pos:
                    raise ValueError(
                        f"Ordre invalide : 'normalization' (position {norm_pos + 1}) "
                        f"doit preceder '{s}' (position {s_pos + 1})."
                    )

        if 'tag_cleaning' in steps and 'normalization' in steps:
            tc_pos = steps.index('tag_cleaning')
            if tc_pos > norm_pos:
                raise ValueError(
                    f"Ordre invalide : 'tag_cleaning' (position {tc_pos + 1}) "
                    f"doit preceder 'normalization' (position {norm_pos + 1})."
                )

    def set_steps(self, steps: List[str]):
        """Configure les etapes du pipeline en verifiant leur validite."""
        for s in steps:
            if s not in self.REGISTRY:
                raise ValueError(
                    f"Etape inconnue : '{s}'. Choisir parmi : {list(self.REGISTRY.keys())}"
                )
        self._validate_order(steps)
        self.steps = list(steps)

    def add_step(self, step_name: str, position: Optional[int] = None):
        """Ajoute une etape et re-verifie la validite globale."""
        new_steps = list(self.steps)
        if position is None:
            new_steps.append(step_name)
        else:
            new_steps.insert(position, step_name)
        self.set_steps(new_steps)

    def remove_step(self, step_name: str):
        """Retire une etape."""
        new_steps = [s for s in self.steps if s != step_name]
        self.set_steps(new_steps)

    def describe(self) -> str:
        """Retourne une representation visuelle de la sequence."""
        return " -> ".join(self.steps)

    def transform(self, input_data: Union[str, List[str]], verbose: bool = False) -> Union[str, List[str]]:
        """Applique l'ensemble des etapes sur un texte ou une liste de tokens."""
        current = input_data
        for step in self.steps:
            func = self.REGISTRY[step]
            if step in self.STR_INPUT_STEPS:
                if isinstance(current, list):
                    current = ' '.join(current)
            else:
                if isinstance(current, str):
                    current = current.split()
            current = func(current)
            if verbose:
                preview = current[:5] if isinstance(current, list) else current[:60]
                print(f"  [{step:>14}] -> {preview}")
        return current

    def fit_transform(self, corpus: Dict[str, str], verbose: bool = False) -> Dict[str, List[str]]:
        """Applique le pipeline a l'ensemble du corpus {doc_id -> raw_text}."""
        processed = {}
        for doc_id, text in corpus.items():
            processed[doc_id] = self.transform(text, verbose=verbose)
        return processed

    def __repr__(self) -> str:
        return f"NLPPipeline(steps={self.steps})"
