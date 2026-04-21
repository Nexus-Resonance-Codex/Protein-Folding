import gradio as gr
import gradio_client.utils

original = gradio_client.utils.json_schema_to_python_type
def safe_json_schema_to_python_type(schema, defs=None):
    try:
        return original(schema, defs)
    except (TypeError, KeyError):
        return "Any"
gradio_client.utils.json_schema_to_python_type = safe_json_schema_to_python_type

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from nrc_engine import NRCEngine
from biophysics import BiophysicsSuite
from reporting import ReportingSuite
import os

# ─── Initialization ──────────────────────────────────────────────────────────
engine = NRCEngine()

# ─── Prototypes / Presets ──────────────────────────────────────────────────
PROTEIN_LIBRARY = {
    "Insulin": {"seq": "GIVEQCCTSICSLYQLENYCNFVNQHLCGSHLVEALYLVCGERGFFYTPKT"},
    "Ubiquitin": {"seq": "MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG"},
    "Lysozyme": {"seq": "KVFERCELARTLKRLGMDGYRGISLANWMCLAKWESGYNTRATNYNAGDRSTDYGIFQINSRYWCNDGKTPGAVNACHLSCSALLQDNIADAVACAKRVVRDPQGIRAWVAWRNRCQNRDVRQYVQGCGV"},
    "BPTI": {"seq": "RPDFCLEPPYTGPCKARIIRYFYNAKAGLCQTFVYGGCRAKRNNFKSAEDCMRTCGGA"},
    "Myoglobin": {"seq": "MGLSDGEWQLVLNVWGKVEADIPGHGQEVLIRLFKGHPETLEKFDKFKHLKSEDEMKASEDLKKHGATVLTALGGILKKKGHHEAEIKPLAQSHATKHKIPVKYLEFISECIIQVLQSKHPGDFGADAQGAMNKALELFRKDMASNYKELGFQG"},
    "p53 DNA-binding": {"seq": "MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPRMPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQKTYQGSYGFRLGFLHSGTAKSVTCTYSPALNKMFCQLAKTCPVQLWVDSTPPPGTRVRAMAIYKQSQHMTEVVRRCPHHERCSDSDGLAPPQHLIRVEGNLRVEYLDDRNTFRHSVVVPYEPPEVGSDCTTIHYNYMCNSSCMGGMNRRPILTIITLEDSSGNLLGRNSFEVRVCACPGRDRRTEEENLRKKGEPHHELPPGSTKRALPNNTSSSPQPKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGSRAHSSHLKSKKGQSTSRHKKLMFKTEGPDSD"},
    "Rhodopsin (GPCR)": {"seq": "MNGTEGPNFYVPFSNKTGVVRSPFEAPQYYLAEPWQFSMLAAYMFLLIMLGFPINFLTLYVTVQHKKLRTPLNYILLNLAVADLFMVFGGFTTTLYTSLHGYFVFGPTGCNLEGFFATLGGEIALWSLVVLAIERYVVVCKPMSNFRFGENHAIMGVAFTWVMALACAAPPLVGWSRYIPEGMQCSCGIDYYTPHEETNNESFVIYMFVVHFIIPLIVIFFCYGQLVFTVKEAAAQQQESATTQKAEKEVTRMVIIMVIAFLICWLPYAGVAFYIFTHQGSDFGPIFMTIPAFFAKTSAVYNPVIYIMMNKQFRNCMVTTLCCGKNPLGDDEASATASKTETSQVAPA"},
    "Top7 (Designed)": {"seq": "MGDIQVQVNIDDNGKNFDYTYTVTTESELQKVLNELMDYIKKQGAKRVRISITARTKKEAEKFAAILIKVFAELGYNDINVTFDGDTVTVEGQLEGGSLEHHHHHH"},
    "ORF8 (SARS-CoV-2)": {"seq": "MKFLVFLGIITTVAAFHQECSLQSCTQHQPYVVDDPCPIHFYSKWYIRVGARKSAPLIELCVDEAGSKSPIQYIDIGNYTVSCLPFTINCQEPKLGSLVVRCSFYEDFLEYHDVRVVLDFI"},
    "TRPV1": {"seq": "MKKWSSTDLGAAADPLQKDTCPDPLDGDPNSRPPPAKPQLSTAKSRTRLFGKGDSEEASPLDCPYEEGGLASCPIITVSSVLTIQRPGDGPASVRAASQDSVAASTEKTLRLYDRRSIFEAVAQNNCQDLESLLLFLQKKSKKLPVDRNIAFRNYDLLFGTTRLCPGNNFEGLVNYGLLVDLHLLLQKKCHLPTTPHCSSTSPVLPTRPTPHCTPTPSTPSTPSTPSTPST"},
    "Abeta42": {"seq": "DAEFRHDSGYEVHHQKLVFFAEDVGSNKGAIIGLMVGGVVIA"},
    "Titinfold": {"seq": "LIEVEKPLYGVEVFVGETAHFEIELSEPDVHGQWKLKGQPLTASPDCEIIEDGKKHILILHNCQLGMTGEVSFQAANTKSAANLKVKEL"},
    "Tough-Target-13": {"seq": "ASFPLDVAPRLCLAVTVAKLGSKASCPAWNLVAAKACMLASKRVRRPLTDLNVKALHSATVLS"},
    "Tough-Target-14": {"seq": "STQLRSALKFKLCCVKKNRHAKYLPEDSALQHFGLHLHPSLMYQKCMLQQVPKHEVLGTHPNLCLALQHISCRTCKVKGPAAAGAYVKPVVHLLLKRVSQLVGMAKK"},
    "Tough-Target-15": {"seq": "QCAREQVKHMALTALQLTHQLAKSGTITNAIHLTTKLGGHSVVLQVAVPALQGLLP"},
    "Tough-Target-16": {"seq": "RCVAAAHAPPGKAASKLVKGLVRPGLHQCVVTDVLNLTCMKHKKKLHHPRHHEKLGCQHLQKKYAATTVR"},
    "Tough-Target-17": {"seq": "KNALRKGHALAVAHGKQWVGKNPCVLATKKTLCAVKRVPKANRCTKRTQSPGVLPCESKPPVADYEARKANHQAVIINAYKAVLCCEAK"},
    "Tough-Target-18": {"seq": "LRSPGKAVNMACFQVPCAQTKSLTKPCLCPSLFCCKKSDAYKVALSIHCKACCGMKCPVKITYPTQAASSNTPALLVPCSLGEHNHLGCVLYRLQLKPCHV"},
    "Tough-Target-19": {"seq": "ADAHLAKYPNGHAQTNVPTPELRQGADVQLTNENGCCVKCQHVAQSCQKCFNAHKAEQKAKRSQVMKSVKKTPAAAKCQTRNNGSWNYALHKPICATNAYKIKTLNVAVLQYHVMTQQNLSHPMRGAHRKAMI"},
    "Tough-Target-20": {"seq": "NLALHHKQMPKCENVLLSNTTGKVLHISAVGCNLQKDLA"},
    "Tough-Target-21": {"seq": "CYFKHWTGCQKMNIALVVDKPHVLKAMPKGKVLASVGKQKHWVSCELPRKYHNSKKAAKPLVGATHFAHQACAMRHHCVALHRIQAVQRKNHLLVTQWLSNVLNEEVSGHPCWRRY"},
    "Tough-Target-22": {"seq": "GTCCWAINCGFDLKVVQHLSGQNRALIDYCKDRCKCNVAPTQPKVLKPGTAKDNTKPHTHPLSQVKRFFKAGHRQGAQHGL"},
    "Tough-Target-23": {"seq": "SEALHVLGKLLVVTRRTKPRCVDGQLYRKLPVGLTSGKCSLKLAVMGWVPRVVNMVMIKFHPACCYAVSNQTTS"},
    "Tough-Target-24": {"seq": "NYRRFCQGDSVYHTKKKAKALGAASSCQSKLLNQKWKNSVDLQAVTKVARVPQQRCKVNIRDHAIQCCRLHAPLYHDIGNVLLK"},
    "Tough-Target-25": {"seq": "KSKQFLCHWIQPNKKWTLLLVHASLFQHGHGANAMPLQLNLALKMAFPNRQRVHVVCNEKELLACARRISKVTSLHG"},
    "Tough-Target-26": {"seq": "HWTLIVWYFHRPVDLHSGRPGNLAVTAARKLSNNLHRKQLDVQTVDCVHWKWCVTHVCWCVMKQTLMSLVGMVSCPLTQRGKFRLL"},
    "Tough-Target-27": {"seq": "VSLGLQTAAVTFMNCPEFQAQAHMKKNSPAFESSTT"},
    "Tough-Target-28": {"seq": "MCVARTKSLLLKKWAGHPHAQSDSGKVHNTVTNKNLPVKSCVFKSFSNVVKHGLYLTTLARKDRLLVVLLWLNHEKHEIVPTAKTVASTHKKFRMLKVHLSTAGPGQALMHTPAFDLLKAHPLFVGMNTGWKGKSLPRLQWKQA"},
    "Tough-Target-29": {"seq": "LKLTGVAQLHKAVQCVKVQPRARVVMNSDCGVPLYKLVARLQVVYPTFKQVSKTLCYVVKPSRTAACCQERNLNPHHFLKNCAEAFKNSVPVLLGCAANHKHHKNGGKLVYPQLWAIACLKYWAMNHKKQAAMVHLSFKRRLAG"},
    "Tough-Target-30": {"seq": "CAVGQPERKVSGSVLKKSNRLRQQEPKALLLLRCGTLRKLESLRCCVKAEKGGSTKPQ"},
    "Tough-Target-31": {"seq": "WSKTHCVNVALAQLILKHAHHKYNALQKKAAGQDTSLVMCTLCSYAGEPKDATVYCLMLPSLQACLLRPDDGLRVPCALALDRQVVRMKVAFSQVRAKVANQLMNVGRFAKRKIKLAVQTAKVVCMDILRCFRSCVVTVQVQAANPK"},
    "Tough-Target-32": {"seq": "LLNLASVRCSKGVKDALAHVVNEQTAKVQMLHWYVTPLCGRWKGWHFHQ"},
    "Tough-Target-33": {"seq": "LDSKWVLMLVRWIGCNPCKVLKAVTVCWKFGKIMDFTWVCFKCVSSVDKLRKRCHLWAANTKTGGVQPVDQYPPNYQSDHLNAKC"},
    "Tough-Target-34": {"seq": "VHSRVMFHCHHLNPRKQASLAMLQWQSPKYNALTQRAAPCLRAQSVPLRLDPMKNRKALHVSYKQ"},
    "Tough-Target-35": {"seq": "SLCCHLKPLKTHKCLLPSKPLPLKGEKARCTPLSSWTPNNPLSNLSSAMLVCVTQHLRASYHADTTQ"},
    "Tough-Target-36": {"seq": "FDGVLALGLLLLALSHLWQKAIKHLAGQLPLNEGYRMAGAAPGKAASRKLVEAAVHRKQGMLPAVPSKMRQLPANHLAVSKQKERCAKAACCPCLPVVHCLKKAVCPPKCLKAKWKAA"},
    "Tough-Target-37": {"seq": "FNAVPHRVTKVHQAWHVGVGCGKQSGHCGDLNENELAKVHVVTHHVTVKVKATLRSLWPGKCRVQTM"},
    "Tough-Target-38": {"seq": "RVAAAPHVKSYNCARNVHFLTGVVKRKQGCAQDLWSMRMYAHQNDKV"},
    "Tough-Target-39": {"seq": "LVALFGKSRPLGKNHGGLWWQEVPLTHTKFGVQGKGLKVMIYLCQILAYVHIKAGKAPSHLTCLVFTLVIGKQILVHVLVRRSARAVLQKTTFRSQSRQYRNVGCIGLTGTTCVTCSKQAHFWVDVRLGNQFPSKK"},
    "Tough-Target-40": {"seq": "HGACRFSSTHPTSRCKPELYQQQFYHWVVLV"},
    "Tough-Target-41": {"seq": "KNIQSVVVRPMPKPTVRAGKASLLYISYYRVVECLGT"},
    "Tough-Target-42": {"seq": "RKLYSTKTRLVDKWGSHYQVLTSGQTVGRVNAVRGHTVKSQSQHQMVGCPCHGNQ"},
    "Tough-Target-43": {"seq": "HSAPPKSLVKPLSVAGCKLVHHALKFGVICLAVAISSNLQNRKALRVQPRTWNAMSKKWYLANFKTEGLAAQTKCARYGPAEGPHEDSCRVHNCVLLQVLVVHKKKGLSALCQFTQRPHQR"},
    "Tough-Target-44": {"seq": "NFVQLHPVCLELHLRVASFWKKKLEQSVKICACAPLPPAGYRLKNAPLALLVKDRANKAQLVVGIAVLLKDEVYALACKGWSAAHAQQGQKAVPTSERDRNADNQQKMPGRHDCAGQLVLCHKTASEVGHVHNLTGLEHVQPR"},
    "Tough-Target-45": {"seq": "NDNIAEHNKMELCAKCQKCVVRAKDSKKARTRPYGKNAHVCKQAPQREQCRPAGLFVTTPVWTKQKHFTNKMVKPTPVTPQVVCGHMGFTDSLLLFKKLGKHGLNAHLVTKCVGKQEWRYRGPKASNRQKVHLS"},
    "Tough-Target-46": {"seq": "QGTWVFNLGKNFLAVKGQGKERCCSIPQYPLLVLKFCAKAALHHPANPPDVTHCALSVVPHAMFAKAGAHNNQPVYK"},
    "Tough-Target-47": {"seq": "HRTNREYGHGPQYNVHLLCHMVLNSKIDACSGAWGLMLSNGSTKL"},
    "Tough-Target-48": {"seq": "VASTALRANTPHCAASLVHTHHGTRHIPKSDGTCPGNHAPVDTLRNGYAYKAKNRLCLVTKIQVVNLSAGKYSKDGEATLKSKNNPWFCGVGAHYQCPGTALTAMTTKVASLKRKFVG"},
    "Tough-Target-49": {"seq": "AKNGVPDHHDKCTSICPNECSLIDPLYNVPAGNNLLSHNAGEYCCAINPNAHCVYLFLKEKCMLTKFVTMAKVSATGLDCTGPNDATSTLKDLGHANPITIWTLHKPVQCPRGVVVHPGCQSLVHAPLTM"},
    "Tough-Target-50": {"seq": "LHVLVRKWWVFCVEQRGDSSEQLGCVLLADQFILECLLKVLTNTPYMQGMAGNPKRACYVLGCILLLMNTAIRCRGWTSPRHENNYNWDHIASCARNGTCFDGLVNKNRKRVHVALVSQASAMK"},
    "Tough-Target-51": {"seq": "CAVRKQVAESDVQYHVLGHAAKKYTMTHRALDVSDAMQKAKVRSCAVKVPRLDTCVHQKFLW"},
    "Tough-Target-52": {"seq": "KGLVFIKAKYKYVARVCIAGWAVFSRPVSKVEACVNGQALGACLMERDSKWPLH"},
    "Tough-Target-53": {"seq": "LYWQMCHAHAGVLLQSAAQSFKQKHAPEQGVKLWHWNMKDHKELVKPWVWCKALNKPVLQATEARLYRSYAKGKLK"},
    "Tough-Target-54": {"seq": "YLESAVLVCLPRHSCRLVRLASLLKPAQRTASPMLATAKCQKNRSKVKLVGTLHSHCKTY"},
    "Tough-Target-55": {"seq": "KVFKRWNHPNCNPALYAVQKVPALQRCGPEKKVALVLALWAADFWHVIRQPLNIAP"},
    "Tough-Target-56": {"seq": "KQVKSAVTVRVPKVSVTLNVRCPKKKFFKLVVDASPVDTTLFRWWQNIFCTPKLNAVLLVKIQQVYVHVCKSKGMVQSVKQDVIQKFVWVVCMRLYGGVLCRLAGACDLARVAHSPV"},
    "Tough-Target-57": {"seq": "KLYEHLVCPGSAAPAYWPNVYKYVAWVVCESEVKRRKVTANFNKVVALKLVVCTVQCFAFVATTQQRCAPLALAACHVAACSSCSAAAVNQPCGKNQHCEYRK"},
    "Tough-Target-58": {"seq": "QVWAKNTCKGGAQLKSGGCSQADGLCSVEDKPSLFDMRLSVSNKLVKCVVTNTSTLKVTKCCHDNTRHKAVALAKRSWAAVVVWRRNVYVAAQYKIPGHCSKLFSTACV"},
    "Tough-Target-59": {"seq": "AGCQPEHQRCRHELQGSSLLANCRHARVVMWPWPDAQRRADLSIWVVALQKKLHCREKAVMSKVQCSTNLGLCDKCSKRLCRPCD"},
    "Tough-Target-60": {"seq": "AHAGLSANFKHALTMDSKRVFAKTTQKLATELKGVCLKRQLAQNPEVQLVYYSPNCNCNVYWLACKAMHLSSTAAKKAPLAHGVAECPHETVACGPPLHRGSGSQTRRSAKRGHDVSICHFCGHKPCCGDVACPP"},
    "Tough-Target-61": {"seq": "LKVCVMQATVCVQLHALVQIYKPSKLWKGMRRVSLLDGRTLAFYLKVRQVQLECLKMSGKEALVAKGVSPSHAKMATQPNAANQGNRAVKKRDCHCPQVGKAATGAVCLCAV"},
    "Tough-Target-62": {"seq": "QADRFIPLQWGHHSVNPLTLSLLYLGFRRNMRTLLKYKAVLHVSKKVTKASQAALLLARPLVQHMWLNAGKARNHAHCCQHASSKVNDVMNNRGKAARRYRGNTVKNKFPLCV"},
    "Tough-Target-63": {"seq": "VLKMKWVLPVANQGRRPIVYKSVQAKLNPLHAKAQMQFPKLTAKCKRLLLRSPLVNI"},
    "Tough-Target-64": {"seq": "RWLTELQALVNHLSDCFAHINWYSDKKAGHGGTFQKMWAQGRIWKRIKCPLQVG"},
    "Tough-Target-65": {"seq": "KACYLNAMHKLKNFTAPPLVTDPSTCHTCGTCNRCTGAQAWKRHILLWWDCDAKAVCV"},
    "Tough-Target-66": {"seq": "GWNQHARDAAHFNTKKFPVACVHWALGVDHVSFKKAGQLHLGMRCILLMQHQLGVAEPAKTEITRAVMFAKSAGNVSHLCCRDMYRQLACKELHLAAHHKIQGKDLASKA"},
    "Tough-Target-67": {"seq": "GWNQHARDAAHFNTKKFPVACVHWALGVDHVSFKKAGQLHLGMRCILLMQHQLGVAEPAKTEITRAVMFAKSAGNVSHLCCRDMYRQLACKELHLAAHHKIQGKDLASKA"},
    "Tough-Target-68": {"seq": "QKKTTVPVETKPSSNMAGGSVHLGSCAPHAHNRAPHVSKVIPMHWCASDLEQVCYVCALLGAKAARTQKVNCVGYA"},
    "Tough-Target-69": {"seq": "AHCNQDKDLLIALHGALMLTEACSVAKANAAKHNLHALNAVKLCKLYGCLALPQQHLVLLIRDVDTHNKRKVREATDSNFPVCTRAL"},
    "Tough-Target-70": {"seq": "MMHMHDLAHQAKMCKKKPATTYATVNAKVNSVQEVWVQGLQRHPKVGTLCAAASKKVLGL"},
    "Tough-Target-71": {"seq": "TLLILATRRVCDCHPNKAYDTQQPRKSRQNYLMWCLQLHSEGQHPLYHPAGPKASVYLNNAKAVQLLRNPQPVAKSELLKQLKKVHVTQPVCILSAFKSVVLFASSSLTAHLEALVIVMHLVVYKQHAVLHDQCNW"},
    "Tough-Target-72": {"seq": "AVAKLTRKCGCRSAPLYLPGRFKRLNLGSCVSKSLVFSNWLNNLPNPPKKAASEVYWSVFKCLKGKAAPGYLYARHHQTARGNKSCGIKDSGHFVQCLGKCVMLMDCILVDGNAPVEVNVYAVRWV"},
    "Tough-Target-73": {"seq": "QAAVACSVVALCCEPNVHAVDPFVLKMHVVQPVTDNHIVKPEIKWASPVCLRGKNF"},
    "Tough-Target-74": {"seq": "LRSQKGCYATLNKCQWWTVKKYALLLKFVTWKPSTVLGCLVGGVHTSLHLVYAQTQVPHKYFVHKKVFTGLHLWRLIGKSKGNIRAVKAWGRALTLKPSVHLAVSPKARKFKACFTYHAQRGCLMHVDVKLQFL"},
    "Tough-Target-75": {"seq": "LSGCNILFQQLETVVRVQQNTTNKHIEKFALVLQWNGSASIVVYYAQVLTHKPAHWCQCNPKINVIHAKKLTKARQHAAHALPLGAGAK"},
    "Tough-Target-76": {"seq": "NGLHPPAPGNNHVYCVRPKPGKRNSAHCPPSYAPASIACLAVKAVCKKPQPYKPKQCHDWTLAYMVPAGNDVWANAPLDNRPCHLYCRS"},
    "Tough-Target-77": {"seq": "ASRQCKQCTYWVSPPSCTNKRSLALLDTVRIVDL"},
    "Tough-Target-78": {"seq": "KITKPVCPQQADVAVLPKPVCCCHNEIQQALPSVRPGSDSPAILAARK"},
    "Tough-Target-79": {"seq": "TMNTVTALGMMAPVELNRRKVVGRVTQCKRTVVPLNCLGSAVVYLALAVKTGVD"},
    "Tough-Target-80": {"seq": "HAVNLLASGGHSQKKSHNVGVLKCQRYLIKNEHPAAKSLVLCCKLFVAQAYAGGVAHSAQHHGTLSPPNGRHCTKQWMKSLKSYPLCQPSPCTPPETLVYHHWNRGSMAAKAACHPEDLNAPSQGDAGLRAMCGLHGK"},
    "Tough-Target-81": {"seq": "QSKAVVLQKATGLSLWKALSDLRQQNRSPNLEGEPNTIFVSGRQHLAVREGLKILRGVCADTTQEGAIMRCSTCHSLTSNQCFAALPQEDKFRKVQLC"},
    "Tough-Target-82": {"seq": "NKQFEAPKNVPHWPTFRIRGLGNMSRPKNAHLFKPLKHDTNAHAYQVNAHYVPAQQGWKNFDKQCQCAQKPNMANTVPFQRCVTCQVETLTVLTG"},
    "Tough-Target-83": {"seq": "ALSKSNLTNLKVKALKHSCTLQVVLVNFKQLTAQAGMEHFCAKLAVKARYVAKVTPCCKMHKITVTPGRPFMDHKLDSAELDKALYKSPESMCTPDEGCDGLDGCLLVATGPLQAKCSVCKA"},
    "Tough-Target-84": {"seq": "TYPQVPLCAWQPVFICSGIKKLWVCGVVGLVNCWHKRFAPPLSCRKLACVCHKFTFLNKEKDATTASVVNSSLVQRKLFWFAGMSLHVVVPAVKLNVPVTKLKAGSTKRCRTFAHACTTHLCALKNAKKDPCAPY"},
    "Tough-Target-85": {"seq": "LLKGWKLLAAVMCPLVICVKGEKMGAVFSKHKNKEAVSHKVCFLPRAQPAEACGSRVKKHRRPPKKCNSLNMNSSKMKLFTFWKAGNACNFKASSVAARALCQMCKAVQVVKHHSMCHYHYTPTENLLRKTGAYKANAYLV"},
    "Tough-Target-86": {"seq": "TNEAAAGKTRPAVQDVMPLVKAGKANKRNHHYVHAQALITLMLGACQNQPVSGELISKYLSHDHSSQGKYLAAALNHLKLCKNQTFRVLGVDSLQCHKKKGGQQWGKTACCYCNNTRAEFVKLNLKMGYKMRAIKENVAPCQKVGHGNV"},
    "Tough-Target-87": {"seq": "GWKLLHITSSQCVKAAVLQLWDCVHHKDRSLCLQRIAGSNGQCASTALSGN"},
    "Tough-Target-88": {"seq": "NGMCTCVSNVSTNSDSVHLSGRQGKLTGRAKTMHQLMSQAVLKQLYIKVVLSLLKAVPRLGTLARHGYGALNEKSSMIPLGPHNCCFMVPAGDAVGQKWTSLCYVAAVKILAFYAVCPKNNDYE"},
    "Tough-Target-89": {"seq": "HKLVVLLPRARQCCAQSCCRSAVVRVGLELKLLAKITQATVMVKCRNTVWWAPKKQNTAVAKKTVPIAKQIAVQRKKNKHACVGNKLACRYSQALSQSKKVGLKAFNVIGFQVTAIECM"},
    "Tough-Target-90": {"seq": "KMQKHHKWVKSDSLTAKKPHLCAHKQRMTAQVCVCKLAQVVAKVFPHKVQTVNNVSVHNHLFKRR"},
    "Tough-Target-91": {"seq": "SKGCNYNFDTGPFELHAVYTSKAYRVIVAPQQKLVVFKHKNYTAKLLLGTTDLDPLNLLGVAGLLVGHTLVCVNKADKTLKRPTAAQAELVL"},
    "Tough-Target-92": {"seq": "EQPGKHNFACQGATTNLVPLLKIVPVAQTDSKCTYNVNLADNNFKLLHCVLDHVWSYHVKHHVRRYKKTMNCVWNKGKKKGQTKATLRKFALLHRVLAVKRPAVKPWQKLGRAVHQLWKASKWVARHNTANIKNLPVLLPDKDDW"},
    "Tough-Target-93": {"seq": "KRLHQKLKLEKVCNNPHPPQTKKVKISYLNTQPVWLKTVCGGKHDHKSIMYDNDPSADMVPVPGVGLTTLAKYLLRKACAAGAAGTFTPNKAALFKLNAAEEVDVFRRTV"},
    "Tough-Target-94": {"seq": "VRRALAYHKQKWVTDLTSTIHMGSVAAPCLGVNVEECLVWQPVRWNTQ"},
    "Tough-Target-95": {"seq": "VLIHVHNSQNLRFAARKAQLSRKKHLRRAKKFQKELVGTNAGSAWNEVCVVGLKCSISSLALVSAHHSKGNKQPVEGFIQILKRQPRLSADPQCRSRHCDVERVPLGSNCAQYVCKP"},
    "Tough-Target-96": {"seq": "NVPPLKPFPTAYGLGVHLGTATPMPVFTNARVATCKHDQVLYMAGSHVWAQAPAEVAQGAAETPLASYAAVKAACHIKGPKLVYNSLPVDGLWTSYKPIKANLSLHCAVQKKPSQHGCGALCWAPLGACALVSPWVLKNCA"},
    "Tough-Target-97": {"seq": "DAQHKQKCPKHGARHPAYLARVQCFLTRHHKMHSACAAASQSNGLNQGKHLSVPVIQVYCKDRVMRCAPNGQLEIQVCAAQPRALRSSPYSDLTAHGETLLVSRSRLNASINCKEFTKPVQQATAPGVAAFTDKLVVKMLWEKLF"},
    "Tough-Target-98": {"seq": "ENCTKKYKCVKTRQVVVRVKTLVNMVVCACQVEHQLVTPKLLKKVQQMSASDNL"},
    "Tough-Target-99": {"seq": "RLHMELHGDNCGNVYAWPKKLESHRNMTTAQCSP"},
    "Tough-Target-100": {"seq": "SPTSCLKLLVQRELVQPCKKLFLHQHCVHAWICAKQLRCHKKHHWTLKAYALLLAAAANFLKCQHGRVGQHLKLKMCAAVCLGLAPGGLVLRKEPKAWTSAGRKGKNVHVKVLAQ"},
    "Tough-Target-101": {"seq": "AMYQGLIARSSAHGKQVPLTQVPGPRNASVQFEYVLLLLLFKSVPLCQPGDKVILVKACPWQLLHGALVKGANGRAVLVAAGTAPAVQYGCNFAVQSVAWDCLKLVLNMFNYGKSDCLLCNDLMHCLAQVKVPHPVTKRAPVACVT"},
}

CSS = """
:root {
    --nrc-gold: #D4AF37;
    --nrc-obsidian: #1A1A1B;
}
.main-header { text-align: center; color: var(--nrc-gold); padding: 2rem; }
.expert-card { background: #2D2D2E; border-left: 4px solid var(--nrc-gold); padding: 1rem; border-radius: 4px; }
.log-console { font-family: 'Courier New', monospace; font-size: 0.8rem; background: #000; color: #0F0; padding: 10px; border-radius: 4px; height: 300px; overflow-y: scroll; border: 1px solid #333; }
footer { display: none !important; }
"""

def get_viewer_html(pdb_str, engine_type="3Dmol", pockets=None):
    if engine_type == "3Dmol":
        pockets_js = ""
        if pockets:
            for p in pockets:
                indices = ",".join(map(str, p["residues"]))
                pockets_js += f"viewer.addSurface($3Dmol.SurfaceType.VDW, {{opacity:0.4, color:'cyan'}}, {{resi:[{indices}]}});\n"
        
        return f"""
        <div id="mol-container" style="height: 500px; width: 100%; position: relative;"></div>
        <script>
            (function() {{
                const container = document.getElementById('mol-container');
                const viewer = $3Dmol.createViewer(container, {{backgroundColor: 'black'}});
                viewer.addModel(`{pdb_str}`, "pdb");
                viewer.setStyle({{}}, {{cartoon: {{color: 'spectrum'}}}});
                {pockets_js}
                viewer.zoomTo();
                viewer.render();
            }})();
        </script>
        """
    else: # NGL
        return f"""
        <div id="ngl-container" style="height: 500px; width: 100%;"></div>
        <script>
            (function() {{
                const stage = new NGL.Stage("ngl-container", {{backgroundColor: "black"}});
                const blob = new Blob([`{pdb_str}`], {{type: 'text/plain'}});
                stage.loadFile(blob, {{ext: "pdb"}}).then(function(o) {{
                    o.addRepresentation("cartoon", {{color: "resname"}});
                    o.autoView();
                }});
            }})();
        </script>
        """

# ─── Handlers ────────────────────────────────────────────────────────────────
def run_nrc_folding(seq, viewer_choice):
    log_history = []
    def log(msg):
        log_history.append(f"[{pd.Timestamp.now().strftime('%H:%M:%S')}] {msg}")
        return "\n".join(log_history)

    try:
        if not seq: return [None]*11
        seq = seq.strip().upper()
        current_logs = log(f"INIT: Resonance-Fold Pipeline v2.6. Target: {seq[:10]}...")
        
        # 1. Fold
        current_logs = log(f"LATTICE: Projecting {len(seq)} AA into φ-manifold...")
        frames = list(engine.fold_sequence(seq))
        final = frames[-1]
        coords = final["coords"]
        current_logs = log(f"CONVERGENCE: TTT-7 stability achieved at {final['stability']:.4f}")
        
        # 2. Analyze
        current_logs = log("BIOPHYSICS: Quantifying Ramachandran manifolds...")
        analysis = BiophysicsSuite.analyze_sequence(seq, coords)
        meta = {
            "hash": ReportingSuite.generate_share_hash(seq),
            "avg_confidence": float(np.mean(final["confidence"])),
            "ttt_stability": float(final["stability"])
        }
        
        # 3. Reports
        current_logs = log("IO: Generating PDB 3.3 research shard...")
        pdb_text = ReportingSuite.generate_pdb(seq, coords)
        zip_path = ReportingSuite.create_research_package(f"nrc_{meta['hash']}", seq, coords, analysis, meta)
        
        # 4. 3D Visualization
        viewer_html = get_viewer_html(pdb_text, viewer_choice, pockets=analysis["pockets"][:1])
        
        # 5. Lattice Explorer
        lattice_viz = go.Figure(data=[go.Scatter3d(
            x=coords[:, 0], y=coords[:, 1], z=coords[:, 2],
            mode='lines+markers', line=dict(color='gold', width=4)
        )])
        lattice_viz.update_layout(template="plotly_dark", title="φ-Lattice Projection")
        
        # 6. Analytics Plots
        h_fig = go.Figure(data=go.Heatmap(z=[analysis["hydropathy"]], colorscale='Viridis'))
        h_fig.update_layout(template="plotly_dark", title="Hydrophobicity Profile", height=200)
        
        c_fig = go.Figure(data=go.Heatmap(z=[analysis["charge"]], colorscale='RdBu', zmid=0))
        c_fig.update_layout(template="plotly_dark", title="Charge Profile", height=200)
        
        summary_df = pd.DataFrame([
            ["Length", len(seq)],
            ["pI", analysis["pI"]],
            ["Stability", f"{meta['ttt_stability']:.4f}"]
        ], columns=["Metric", "Value"])
        
        current_logs = log("SUCCESS: Institutional package ready for export.")
        return (
            viewer_html, lattice_viz, h_fig, c_fig, summary_df, 
            zip_path, pdb_text, "".join(analysis["dssp"]), analysis["pI"], meta["hash"], current_logs
        )
    except Exception as e:
        import traceback
        err_msg = log(f"ERROR: {str(e)}")
        print(f"PIPELINE ERROR: {e}")
        traceback.print_exc()
        raise gr.Error(f"Institutional Error: {str(e)}")

# ─── App UI ──────────────────────────────────────────────────────────────────
HEAD_HTML = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/3Dmol/2.4.2/3Dmol-min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/ngl@2.0.0-dev.37/dist/ngl.js"></script>
"""

with gr.Blocks(css=CSS, title="Resonance-Fold") as demo:
    
    gr.HTML("<div class='main-header'><h1>RESONANCE-FOLD</h1></div>")
    
    with gr.Tabs():
        with gr.Tab("🔬 Playground"):
            with gr.Row():
                with gr.Column(scale=1):
                    seq_input = gr.Textbox(label="Sequence", lines=8, placeholder="Paste FASTA or raw amino acid sequence...")
                    viewer_choice = gr.Radio(["3Dmol", "NGL"], label="3D Engine", value="3Dmol")
                    fold_btn = gr.Button("🚀 EXECUTE", variant="primary")
                    
                    with gr.Accordion("Grand Gallery (Top 100 Difficult Targets)", open=False):
                        target_select = gr.Dropdown(
                            choices=list(PROTEIN_LIBRARY.keys()),
                            label="Select Research Target",
                            interactive=True
                        )
                        load_target_btn = gr.Button("📥 LOAD TARGET", size="sm")
                        
                        def load_selected_target(name):
                            if name in PROTEIN_LIBRARY:
                                return PROTEIN_LIBRARY[name]["seq"]
                            return ""
                        
                        target_select.change(load_selected_target, target_select, seq_input)
                        target_select.select(load_selected_target, target_select, seq_input)
                        load_target_btn.click(load_selected_target, target_select, seq_input)
                
                with gr.Column(scale=2):
                    viewer_box = gr.HTML("<div style='height: 520px; border: 1px dashed #444; border-radius: 8px; display: flex; align-items: center; justify-content: center;'>Fold a protein to see the 3D structure here.</div>")
                    log_console = gr.Textbox(label="Institutional Log Console", lines=10, elem_classes="log-console", interactive=False)
        
        with gr.Tab("📊 Analytics"):
            with gr.Row():
                hydro_plot = gr.Plot(label="Hydrophobicity")
                charge_plot = gr.Plot(label="Charge")
            summary_table = gr.Dataframe(label="Analysis Summary")
            
        with gr.Tab("🧬 Expert Suite"):
            with gr.Row():
                lattice_plot = gr.Plot(label="φ-Lattice Explorer")
                with gr.Column():
                    dssp_out = gr.Textbox(label="DSSP Assignment", interactive=False)
                    pi_out = gr.Number(label="Isoelectric Point (pI)", interactive=False)
                    hash_out = gr.Textbox(label="Provenance Hash", interactive=False)
        
        with gr.Tab("📦 Export"):
            export_file = gr.File(label="Download Research Package (.zip)")
            raw_pdb = gr.Code(label="PDB 3.3 Output", language="markdown")
            
        with gr.Tab("📚 Documentation"):
            gr.Markdown("""
            ### Institutional Protocol
            Resonance-Fold utilizes the **Nexus Resonance Codex (NRC)** framework to simulate protein structural behavior in high-dimensional φ-manifolds.
            """)

    fold_btn.click(
        fn=run_nrc_folding,
        inputs=[seq_input, viewer_choice],
        outputs=[viewer_box, lattice_plot, hydro_plot, charge_plot, summary_table, export_file, raw_pdb, dssp_out, pi_out, hash_out, log_console]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_api=False,      # Prevents the previous json_schema bool error
        show_error=True,
        quiet=True
    )
