/**
 * Default query function
 *
 * @param options The queryKey to use
 * @returns The response data
 */
export async function queryFn<ResultType>({ queryKey }: { queryKey: string[] }): Promise<ResultType> {
  const response = await window.fetch("/api/" + queryKey.join(""));
  if (response.ok) {
    return response.json();
  } else {
    throw new Error("An error occurred (" + response.status + ")", {
      cause: await response.json(),
    });
  }
}
