import unittest
import Analyzier
import wikiParser


class MyTestCase(unittest.TestCase):
    def test_match(self):
        patterns = Analyzier.generate_patterns("$Emigrate –& name(birthdate–deathDate), Profession$, callsign&")
        print(patterns)
        print(Analyzier.match_pattern(patterns, "1846 – Hermann Ferdinand Rogalla von Bieberstein (1824–1907), "
                                                "Geodät (Schlesien)"))

    def text_extraction_pattern(self):
        pattern = Analyzier.apply("Chet Atkins (1924–2001), US-amerikanischer Country-Musiker, W4CGP", 3)
        print(pattern)


if __name__ == '__main__':
    unittest.main()
