export function formatBytes(bytes:number): string { const units=['B','KiB','MiB','GiB','TiB']; let n=bytes,i=0; while(n>=1024&&i<units.length-1){n/=1024;i++;} return `${n.toFixed(i?2:0)} ${units[i]}`; }
export function cacheKey(mediaId:string): string { return `media/${mediaId}`; }
