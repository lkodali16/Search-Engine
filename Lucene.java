import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.core.SimpleAnalyzer;
import org.apache.lucene.document.*;
import org.apache.lucene.document.Field;
import org.apache.lucene.index.*;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopScoreDocCollector;
import org.apache.lucene.store.*;

import java.io.*;
import java.nio.file.Paths;

public class Main {


    public static final String FIELD_NAME = "name";
    public static final String FIELD_CONTENTS = "contents";

    public static final String DATA_DIRECTORY =
            "tokens";
    public static final String INDEX_DIRECTORY =
            "lucene_index";

    public static void main (String[] args) throws IOException, ParseException {

        buildIndex(INDEX_DIRECTORY, DATA_DIRECTORY);

        String fileName="query_list.txt";

        try{

            //Create object of FileReader
            FileReader inputFile = new FileReader(fileName);

            //Instantiate the BufferedReader Class
            BufferedReader bufferReader = new BufferedReader(inputFile);
            String line;
            //Variable to hold the one line data


            // Read file line by line and call search function on each query
            int query_id = 1;
            while ((line = bufferReader.readLine()) != null) {
                search(INDEX_DIRECTORY, line, query_id);
                query_id++;
            }
            //Close the buffer reader
            bufferReader.close();
        }catch(Exception e) {
            System.out.println("Error while reading file line by line:" + e.getMessage());
        }
    }

    private static void buildIndex(String indexDirectory, String dataDirectory)
            throws IOException {
        deleteDir(new File(indexDirectory));

        Analyzer luceneAnalyzer = new SimpleAnalyzer();
        IndexWriterConfig config = new IndexWriterConfig(luceneAnalyzer);

        IndexWriter indexWriter = new IndexWriter(new SimpleFSDirectory
                (Paths.get(indexDirectory)), config);

        File rawDir = new File(dataDirectory);

        for (File file : rawDir.listFiles()) {

            Document document = new Document();

            String name = file.getName();
            document.add(new Field(FIELD_NAME, name, new FieldType(TextField
                    .TYPE_STORED)));

            document.add(new Field(FIELD_CONTENTS, new FileReader(file), new FieldType
                    (TextField.TYPE_NOT_STORED)));

            indexWriter.addDocument(document);
        }

        indexWriter.close();
    }

    private static void search(String indexDirectory, String queryString, int query_id) throws IOException, ParseException {
        Analyzer luceneAnalyzer = new SimpleAnalyzer();

        IndexReader reader = DirectoryReader.open(new SimpleFSDirectory
                (Paths.get(indexDirectory)));
        IndexSearcher searcher = new IndexSearcher(reader);


        TopScoreDocCollector collector = TopScoreDocCollector.create(100);

        Query q = new QueryParser(FIELD_CONTENTS,
                luceneAnalyzer).parse(queryString);
        searcher.search(q, collector);
        ScoreDoc[] hits = collector.topDocs().scoreDocs;

        printResult(hits, queryString, searcher, query_id);
    }

    public static boolean deleteDir(File dir)
    {
        if (dir.isDirectory())
        {
            String[] children = dir.list();
            for (int i=0; i<children.length; i++)
                return deleteDir(new File(dir, children[i]));
        }
        return dir.delete();
    }

    public static void printResult(ScoreDoc[] hits, String queryString, IndexSearcher searcher, int query_id)
    {
        try{
            BufferedWriter writer = null;

            File file = new File("lucene_out.txt");
            file.createNewFile();

            writer = new BufferedWriter(new FileWriter(file, true));
            writer.write( "Search result for " + queryString + ", " + hits
                    .length + " results.\n");

            int count = 1;
            for (ScoreDoc sd : hits) {
                Document d = searcher.doc(sd.doc);
                writer.write("\n" + query_id + "\tQ0\t" + d.get(FIELD_NAME) + "\t" + count + "\t" + sd.score + "\tLucene_retrieval_system");
                count++;
            }
            writer.write("\n\n");
            writer.close();
        } catch (IOException e) {
            // do something
        }

    }
}