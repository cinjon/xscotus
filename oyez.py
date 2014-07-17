import bs4
import urllib2

baseurl = 'http://www.oyez.org'
basexml = baseurl + '/sites/default/files'

def get_year_cases(year):
    soup = bs4.BeautifulSoup(urllib2.urlopen(urllib2.Request(baseurl + '/cases/' + year)))
    return soup.findAll('tr', {'class':'even'}) + soup.findAll('tr', {'class':'odd'})

def get_data_from_case(case):
    try:
        return case.find('td', {'class':'views-field-field-docket-value'}).getText().strip(), case.find('td', {'class':'views-field-title'}).find('a').attrs.get('href')
    except Exception, e:
        return None, None

def get_transcript_turns(href):
    #href is the href of the case
    case_soup = bs4.BeautifulSoup(urllib2.urlopen(urllib2.Request(baseurl + href)))
    transcript_xml_href = case_soup.find('a', {'class':'audio', 'href':href + '/argument'})
    if transcript_xml_href:
        return bs4.BeautifulSoup(urllib2.urlopen(urllib2.Request(basexml + transcript_xml_href.attrs.get('rel')[0])), features="xml").findAll('turn')
    else:
        return None

def scrape_oyez(years=None):
    years = years or [str(y) for y in range(1980, 2013)] #1980 ... 2012
    years += [s + '?page=1' for s in years]
    years.sort()
    cases = []
    for year in years:
        print year
        for num, year_case in enumerate(get_year_cases(year)):
            docket_num, href = get_data_from_case(year_case)
            case = {'year':year, 'transcript':[], 'docket_num':docket_num}
            if not docket_num or not href:
                print 'No docket_num / href for %d in year %s' % (num, year)
                cases.append(case)
                continue
            turns = get_transcript_turns(href)
            if not turns:
                print 'No Transcript for %s' % docket_num
                case['transcript'] = None
                cases.append(case)
                continue
            for turn_num, turn in enumerate(turns):
                try:
                    speaker = turn.attrs.get('speaker')
                    label = turn.find('label').getText()
                    speech = ' '.join([text.getText() for text in turn.findAll('text')])
                    case['transcript'].append({'speaker':speaker, 'label':label, 'speech':speech})
                except Exception, e:
                    print 'Bad label/speech in turn %d for href %s' % (turn_num, href)
                    case['transcript'].append({})
            cases.append(case)
    return cases
