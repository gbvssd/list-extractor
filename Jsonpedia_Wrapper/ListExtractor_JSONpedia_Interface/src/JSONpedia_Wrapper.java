import java.io.FileNotFoundException;
import java.util.List;

import com.beust.jcommander.*;
import com.beust.*;
import com.machinelinking.main.JSONpedia;
import com.machinelinking.main.JSONpediaException;
import com.machinelinking.wikimedia.WikiPage;
import org.codehaus.jackson.JsonNode;

/** The main wrapper class for JSONpedia written for GSoC 2017 List-Extractor project. 
 * 
 * @author Krishanu Konar
 * @version 1.0
 */
public class JSONpedia_Wrapper {

	/** Main method to take the commandline parameters and make appropriate calls to Jsonpedia.
	 * Prints the output on stdout.
	 * 
	 * @param args commandline arguments.
	 * @throws JSONpediaException
	 * @throws FileNotFoundException
	 */
	public static void main(String[] args) throws JSONpediaException, FileNotFoundException {

		ArgParser parser = new ArgParser();
		new JCommander(parser, args);

		//parsed parameters
		String lang = parser.getLang();
		String resource_name = parser.getResourceName();
		String resource = lang + ":" + resource_name;
		String processors = "" , filters = "";
		List<String> procs = parser.getProcs();
		List<String> fltr = parser.getFilters();
		
		//creating final flags to be passed to Jsonpedia
		for(String s: procs){
			processors += s + ",";
		}
		processors = processors.substring(0, processors.length()-1);
		//System.out.println(processors);
		
		//creating final filters to be passed to Jsonpedia
		if(!(fltr.isEmpty())){
			for(String s: fltr){
				filters += "@type:" + s + ",";
			}
			filters = filters.substring(0,filters.length()-1);
			//System.out.println(filters);
		}
		
		//make a Jsonpedia instance and query with given parameters
		JSONpedia jsonpedia = JSONpedia.instance();
		//System.out.println(resource);
		JsonNode node = jsonpedia.process(resource).flags(processors).
				filter(filters).json();

		System.out.println(node);
	}


}