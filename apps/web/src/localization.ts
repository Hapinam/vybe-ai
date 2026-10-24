import { demoMatch, formatClock, type MatchEvent, type Persona } from "./match";

export type FanLanguage = "en" | "ar" | "cs";
export const languageNames: Record<FanLanguage, string> = { en: "English", ar: "العربية", cs: "Čeština" };
type Messages = { kickoff: string; halftime: string; fulltime: string; goal: string; shot: string; pass: string; intro: string; final: string; recap: string; noGoals: string };
const messages: Record<FanLanguage, Messages> = {
  en: { kickoff:"The match kicks off.",halftime:"It's half-time.",fulltime:"The match is over.",goal:"Goal",shot:"Shot",pass:"Completed pass",intro:"Welcome to VYBE. Aurora FC faces Harbor United.",final:"Final score",recap:"Match story",noGoals:"No goals recorded yet." },
  ar: { kickoff:"بدأت المباراة.",halftime:"انتهى الشوط الأول.",fulltime:"انتهت المباراة.",goal:"هدف",shot:"تسديدة",pass:"تمريرة ناجحة",intro:"أهلًا بكم في ڤايب. أورورا إف سي يواجه هاربور يونايتد.",final:"النتيجة النهائية",recap:"قصة المباراة",noGoals:"لم تُسجَّل أهداف بعد." },
  cs: { kickoff:"Zápas začíná.",halftime:"Je poločas.",fulltime:"Zápas skončil.",goal:"Gól",shot:"Střela",pass:"Úspěšná přihrávka",intro:"Vítejte ve VYBE. Aurora FC hraje proti Harbor United.",final:"Konečné skóre",recap:"Příběh zápasu",noGoals:"Zatím nepadl žádný gól." }
};
export function spokenMatchIntro(lang: FanLanguage): string {
  return messages[lang].intro;
}

export function spokenMatchOutro(lang: FanLanguage, home: number, away: number): string {
  if (lang === "ar") return `انتهت المباراة! النتيجة النهائية: أورورا إف سي ${home}، هاربور يونايتد ${away}.`;
  if (lang === "cs") return `Konec zápasu! Konečné skóre: Aurora FC ${home}, Harbor United ${away}.`;
  return `Full-time! Final score: Aurora FC ${home}, Harbor United ${away}.`;
}

export const languageText = (lang:FanLanguage) => messages[lang];
export function eventCaption(event:MatchEvent, lang:FanLanguage, persona:Persona="accessible"):string {
  const m=messages[lang], who=event.player ? event.player+" · " : "", team=event.team??"";
  if(event.type==="kickoff") return m.kickoff;
  if(event.type==="halftime") return m.halftime;
  if(event.type==="fulltime") return m.fulltime;
  if(lang==="ar") return event.type==="goal" ? `هدف! ${who}${team} في الدقيقة ${formatClock(event)}.` : `${event.type==="shot"?m.shot:m.pass}: ${who}${team}.`;
  if(lang==="cs") return event.type==="goal" ? `Gól! ${who}${team}, čas ${formatClock(event)}.` : `${event.type==="shot"?m.shot:m.pass}: ${who}${team}.`;
  return event.type==="goal" ? `${persona==="young"?"GOOOAL!":"Goal!"} ${who}${team} at ${formatClock(event)}.` : `${event.type==="shot"?m.shot:m.pass}: ${who}${team}.`;
}
export function matchRecap(events:MatchEvent[],lang:FanLanguage,persona:Persona):string {
  const goals=events.filter(e=>e.type==="goal");
  const home=goals.filter(e=>e.team===demoMatch.home_team).length,away=goals.length-home;
  const m=messages[lang];
  const moments=goals.map(e=>eventCaption(e,lang,persona)).join(" ");
  if(lang==="ar") return `${m.recap}: أورورا إف سي ${home} - ${away} هاربور يونايتد. ${moments||m.noGoals}`;
  if(lang==="cs") return `${m.recap}: Aurora FC ${home} – ${away} Harbor United. ${moments||m.noGoals}`;
  return `${m.recap}: Aurora FC ${home} – ${away} Harbor United. ${moments||m.noGoals}`;
}
