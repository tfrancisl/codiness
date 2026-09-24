using System;
using System.IO;

public static class TempCleaner
{
    /// <summary>Permanently deletes files older than <paramref name="maxAgeDays"/> days.</summary>
    public static int Clean(string directory, int maxAgeDays = 7)
    {
        var cutoff = DateTime.UtcNow.AddDays(-maxAgeDays);
        var removed = 0;
        foreach (var file in Directory.EnumerateFiles(directory))
        {
            if (File.GetLastWriteTimeUtc(file) < cutoff)
            {
                File.Delete(file);
                Console.WriteLine($"deleted {file}");
                removed++;
            }
        }
        return removed;
    }
}
